"""Azure Blob Storage helper for CivicSignal evidence uploads.

Required environment variables:
  AZURE_STORAGE_CONNECTION_STRING
  AZURE_STORAGE_CONTAINER (default: civic-evidence)

Use a private container. The application should authorize every upload before
calling upload_evidence(). Never accept a client-supplied blob URL.
"""
import os
import uuid
from pathlib import Path
from azure.storage.blob import BlobServiceClient, ContentSettings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024

def upload_evidence(file_storage, complaint_id: int, uploader_id: int) -> dict:
    if not file_storage or not file_storage.filename:
        raise ValueError("Please select an image.")
    ext = Path(file_storage.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Only JPG, PNG and WEBP images are allowed.")
    content_type = (file_storage.mimetype or "").lower()
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Unsupported image content type.")

    raw = file_storage.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError("Image must be 5 MB or smaller.")
    if not raw:
        raise ValueError("The selected image is empty.")

    # Basic file-signature checks; production deployments should also scan files.
    signatures = {
        ".jpg": (b"\xff\xd8\xff",),
        ".jpeg": (b"\xff\xd8\xff",),
        ".png": (b"\x89PNG\r\n\x1a\n",),
        ".webp": (b"RIFF",),
    }
    if not any(raw.startswith(sig) for sig in signatures[ext]):
        raise ValueError("The file content does not match its extension.")
    if ext == ".webp" and raw[8:12] != b"WEBP":
        raise ValueError("Invalid WEBP image.")

    connection = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection:
        raise RuntimeError("Azure Storage is not configured.")
    container = os.getenv("AZURE_STORAGE_CONTAINER", "civic-evidence")
    service = BlobServiceClient.from_connection_string(connection)
    container_client = service.get_container_client(container)
    try:
        container_client.create_container()
    except Exception:
        # Existing container is expected; deployment identity must have access.
        pass

    blob_name = f"complaints/{complaint_id}/{uploader_id}/{uuid.uuid4().hex}{ext}"
    blob = container_client.get_blob_client(blob_name)
    blob.upload_blob(
        raw,
        overwrite=False,
        content_settings=ContentSettings(content_type=content_type),
    )
    # Store container + blob name in DB, not a public URL or SAS token.
    return {"container": container, "blob_name": blob_name, "content_type": content_type,
            "size_bytes": len(raw)}
