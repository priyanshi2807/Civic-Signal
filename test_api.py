import pytest
from app import create_app, db, User, Category

@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file.as_posix()}")
    monkeypatch.setenv("FLASK_SECRET_KEY", "test-only-secret-key-change-me")
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        db.create_all()
        db.session.add(Category(name="Road and pothole", description="Road damage"))
        db.session.commit()
    with app.test_client() as test_client:
        yield test_client
    with app.app_context():
        db.drop_all()

def register(client, email):
    return client.post("/api/auth/register", json={
        "full_name": "Test Citizen", "email": email,
        "password": "A-long-test-password-123"
    })

def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json["database"] == "connected"

def test_registration_and_duplicate_email(client):
    assert register(client, "one@example.test").status_code == 201
    assert register(client, "one@example.test").status_code == 409

def test_citizen_can_create_and_list_complaint(client):
    assert register(client, "citizen@example.test").status_code == 201
    login = client.post("/api/auth/login", json={
        "email": "citizen@example.test", "password": "A-long-test-password-123"
    })
    assert login.status_code == 200
    created = client.post("/api/complaints", json={
        "category_id": 1, "title": "Test pothole",
        "description": "A test report for automated tests.",
        "location_text": "Test Lane", "priority": "high"
    })
    assert created.status_code == 201
    assert created.json["tracking_code"].startswith("CS-")
    listed = client.get("/api/complaints")
    assert listed.status_code == 200
    assert len(listed.json) == 1

def test_admin_endpoint_denied_to_citizen(client):
    register(client, "citizen2@example.test")
    client.post("/api/auth/login", json={
        "email": "citizen2@example.test", "password": "A-long-test-password-123"
    })
    response = client.get("/api/admin/analytics")
    assert response.status_code == 403
