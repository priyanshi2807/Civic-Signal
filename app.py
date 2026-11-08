import os
from datetime import datetime, timezone
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
db = SQLAlchemy()
login_manager = LoginManager()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("citizen", "staff", "admin", name="user_roles"),
                     nullable=False, default="citizen")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    complaints = db.relationship("Complaint", back_populates="reporter",
                                 foreign_keys="Complaint.reporter_id")

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

class Complaint(db.Model):
    __tablename__ = "complaints"
    id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(24), unique=True, nullable=False, index=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location_text = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Numeric(9, 6))
    longitude = db.Column(db.Numeric(9, 6))
    priority = db.Column(db.Enum("low", "medium", "high", name="priority_levels"),
                         nullable=False, default="medium")
    status = db.Column(db.Enum("submitted", "acknowledged", "assigned", "in_progress",
                               "resolved", "verified", "reopened", "rejected",
                               name="complaint_statuses"),
                       nullable=False, default="submitted", index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    reporter = db.relationship("User", back_populates="complaints", foreign_keys=[reporter_id])
    category = db.relationship("Category")
    assignments = db.relationship("Assignment", back_populates="complaint")
    history = db.relationship("StatusHistory", back_populates="complaint",
                              order_by="StatusHistory.changed_at")

class Assignment(db.Model):
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=False, index=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    assigned_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    note = db.Column(db.String(500))
    complaint = db.relationship("Complaint", back_populates="assignments")
    staff = db.relationship("User", foreign_keys=[staff_id])

class StatusHistory(db.Model):
    __tablename__ = "status_history"
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=False, index=True)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    old_status = db.Column(db.String(30))
    new_status = db.Column(db.String(30), nullable=False)
    note = db.Column(db.String(500))
    changed_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    complaint = db.relationship("Complaint", back_populates="history")

class Evidence(db.Model):
    __tablename__ = "evidence"
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=False, index=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    evidence_type = db.Column(db.Enum("before", "after", "other", name="evidence_types"),
                              nullable=False, default="other")
    blob_url = db.Column(db.String(700), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class Verification(db.Model):
    __tablename__ = "verifications"
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=False, index=True)
    verified_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    result = db.Column(db.Enum("confirmed_fixed", "still_unresolved", name="verification_results"),
                       nullable=False)
    comment = db.Column(db.String(1000))
    verified_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class ActivityLog(db.Model):
    __tablename__ = "activity_logs"
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(60), nullable=False)
    entity_id = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                return jsonify(error="You are not authorized for this action."), 403
            return fn(*args, **kwargs)
        return wrapped
    return decorator

def log_activity(action, entity_type, entity_id=None):
    db.session.add(ActivityLog(
        actor_id=current_user.id if current_user.is_authenticated else None,
        action=action, entity_type=entity_type, entity_id=entity_id,
        ip_address=request.remote_addr
    ))

def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "local-development-only-change-me"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///civicsignal.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        MAX_CONTENT_LENGTH=5 * 1024 * 1024
    )
    db.init_app(app)
    login_manager.init_app(app)

    @app.get("/")
    def home():
        return jsonify(
            project="CivicSignal",
            status="running",
            message="Civic issue reporting and resolution verification API",
            api_version="1.0"
        )

    @app.get("/api/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify(status="healthy", database="connected")
        except Exception:
            app.logger.exception("Database health check failed")
            return jsonify(status="degraded", database="unavailable"), 503

    @app.post("/api/auth/register")
    def register():
        data = request.get_json(silent=True) or {}
        name, email, password = (data.get("full_name", "").strip(),
                                 data.get("email", "").strip().lower(),
                                 data.get("password", ""))
        if not name or not email or len(password) < 10:
            return jsonify(error="Name, email and a password of at least 10 characters are required."), 400
        if User.query.filter_by(email=email).first():
            return jsonify(error="An account with this email already exists."), 409
        # Public registration can only create citizen accounts.
        user = User(full_name=name, email=email,
                    password_hash=generate_password_hash(password), role="citizen")
        db.session.add(user)
        db.session.commit()
        return jsonify(message="Registration successful. Please log in.", user_id=user.id), 201

    @app.post("/api/auth/login")
    def login():
        data = request.get_json(silent=True) or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        user = User.query.filter_by(email=email, is_active=True).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify(error="Invalid email or password."), 401
        login_user(user)
        log_activity("login", "user", user.id)
        db.session.commit()
        return jsonify(message="Login successful", user={
            "id": user.id, "full_name": user.full_name, "role": user.role
        })

    @app.post("/api/auth/logout")
    @login_required
    def logout():
        log_activity("logout", "user", current_user.id)
        db.session.commit()
        logout_user()
        return jsonify(message="Logged out successfully")

    @app.get("/api/me")
    @login_required
    def me():
        return jsonify(id=current_user.id, full_name=current_user.full_name,
                       email=current_user.email, role=current_user.role)

    @app.get("/api/categories")
    def categories():
        return jsonify([{"id": c.id, "name": c.name, "description": c.description}
                        for c in Category.query.order_by(Category.name).all()])

    @app.post("/api/complaints")
    @role_required("citizen")
    def create_complaint():
        data = request.get_json(silent=True) or {}
        required = ["category_id", "title", "description", "location_text"]
        if any(not data.get(k) for k in required):
            return jsonify(error="category_id, title, description and location_text are required."), 400
        category = db.session.get(Category, data["category_id"])
        if not category:
            return jsonify(error="Invalid complaint category."), 400
        import secrets
        complaint = Complaint(
            tracking_code="CS-" + secrets.token_hex(5).upper(),
            reporter_id=current_user.id, category_id=category.id,
            title=data["title"].strip()[:140], description=data["description"].strip(),
            location_text=data["location_text"].strip()[:255],
            priority=data.get("priority", "medium")
        )
        db.session.add(complaint)
        db.session.flush()
        db.session.add(StatusHistory(complaint_id=complaint.id, changed_by=current_user.id,
                                     old_status=None, new_status="submitted",
                                     note="Complaint submitted"))
        log_activity("complaint_created", "complaint", complaint.id)
        db.session.commit()
        return jsonify(message="Complaint submitted", id=complaint.id,
                       tracking_code=complaint.tracking_code, status=complaint.status), 201

    @app.get("/api/complaints")
    @login_required
    def list_complaints():
        query = Complaint.query
        if current_user.role == "citizen":
            query = query.filter_by(reporter_id=current_user.id)
        elif current_user.role == "staff":
            assigned_ids = db.session.query(Assignment.complaint_id).filter_by(
                staff_id=current_user.id)
            query = query.filter(Complaint.id.in_(assigned_ids))
        rows = query.order_by(Complaint.created_at.desc()).limit(100).all()
        return jsonify([{
            "id": c.id, "tracking_code": c.tracking_code, "title": c.title,
            "category": c.category.name, "location": c.location_text,
            "status": c.status, "priority": c.priority,
            "created_at": c.created_at.isoformat()
        } for c in rows])

    @app.get("/api/complaints/<int:complaint_id>")
    @login_required
    def complaint_detail(complaint_id):
        c = db.session.get(Complaint, complaint_id)
        if not c:
            return jsonify(error="Complaint not found."), 404
        if current_user.role == "citizen" and c.reporter_id != current_user.id:
            return jsonify(error="Not authorized."), 403
        if current_user.role == "staff" and not Assignment.query.filter_by(
                complaint_id=c.id, staff_id=current_user.id).first():
            return jsonify(error="Not authorized."), 403
        return jsonify(
            id=c.id, tracking_code=c.tracking_code, title=c.title,
            description=c.description, category=c.category.name,
            location=c.location_text, status=c.status, priority=c.priority,
            history=[{"old": h.old_status, "new": h.new_status,
                      "note": h.note, "at": h.changed_at.isoformat()} for h in c.history]
        )

    @app.post("/api/complaints/<int:complaint_id>/assign")
    @role_required("admin")
    def assign_complaint(complaint_id):
        data = request.get_json(silent=True) or {}
        c = db.session.get(Complaint, complaint_id)
        staff = db.session.get(User, data.get("staff_id"))
        if not c or not staff or staff.role != "staff":
            return jsonify(error="Complaint or staff account not found."), 404
        db.session.add(Assignment(complaint_id=c.id, staff_id=staff.id,
                                  assigned_by=current_user.id, note=data.get("note")))
        old = c.status
        c.status = "assigned"
        db.session.add(StatusHistory(complaint_id=c.id, changed_by=current_user.id,
                                     old_status=old, new_status="assigned",
                                     note="Assigned to municipal staff"))
        log_activity("complaint_assigned", "complaint", c.id)
        db.session.commit()
        return jsonify(message="Complaint assigned", status=c.status)

    @app.patch("/api/complaints/<int:complaint_id>/status")
    @role_required("staff", "admin")
    def update_status(complaint_id):
        data = request.get_json(silent=True) or {}
        allowed = {"acknowledged", "in_progress", "resolved", "reopened"}
        new_status = data.get("status")
        if new_status not in allowed:
            return jsonify(error="Unsupported status."), 400
        c = db.session.get(Complaint, complaint_id)
        if not c:
            return jsonify(error="Complaint not found."), 404
        if current_user.role == "staff" and not Assignment.query.filter_by(
                complaint_id=c.id, staff_id=current_user.id).first():
            return jsonify(error="Not authorized."), 403
        old = c.status
        c.status = new_status
        db.session.add(StatusHistory(complaint_id=c.id, changed_by=current_user.id,
                                     old_status=old, new_status=new_status,
                                     note=data.get("note", "")[:500]))
        log_activity("status_changed", "complaint", c.id)
        db.session.commit()
        return jsonify(message="Status updated", old_status=old, status=new_status)

    @app.post("/api/complaints/<int:complaint_id>/verify")
    @role_required("citizen", "admin")
    def verify_complaint(complaint_id):
        data = request.get_json(silent=True) or {}
        result = data.get("result")
        if result not in {"confirmed_fixed", "still_unresolved"}:
            return jsonify(error="result must be confirmed_fixed or still_unresolved."), 400
        c = db.session.get(Complaint, complaint_id)
        if not c or (current_user.role == "citizen" and c.reporter_id != current_user.id):
            return jsonify(error="Complaint not found or not authorized."), 404
        if c.status != "resolved":
            return jsonify(error="Only resolved complaints can be verified."), 409
        db.session.add(Verification(complaint_id=c.id, verified_by=current_user.id,
                                    result=result, comment=data.get("comment", "")[:1000]))
        old = c.status
        c.status = "verified" if result == "confirmed_fixed" else "reopened"
        db.session.add(StatusHistory(complaint_id=c.id, changed_by=current_user.id,
                                     old_status=old, new_status=c.status,
                                     note="Verification: " + result))
        log_activity("complaint_verified", "complaint", c.id)
        db.session.commit()
        return jsonify(message="Verification recorded", status=c.status)

    @app.get("/api/admin/analytics")
    @role_required("admin")
    def analytics():
        total = Complaint.query.count()
        by_status = db.session.query(Complaint.status, db.func.count(Complaint.id)).group_by(
            Complaint.status).all()
        by_category = db.session.query(Category.name, db.func.count(Complaint.id)).join(
            Complaint, Complaint.category_id == Category.id).group_by(Category.name).all()
        return jsonify(total_complaints=total,
                       by_status={status: count for status, count in by_status},
                       by_category={name: count for name, count in by_category})

    @app.errorhandler(413)
    def too_large(_):
        return jsonify(error="Request exceeds the 5 MB limit."), 413

    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if Category.query.count() == 0:
            db.session.add_all([
                Category(name="Road and pothole", description="Damaged roads and potholes"),
                Category(name="Waste management", description="Garbage and sanitation"),
                Category(name="Water supply", description="Leaks and water supply issues"),
                Category(name="Street lighting", description="Broken or missing streetlights"),
                Category(name="Drainage", description="Blocked drains and waterlogging")
            ])
            db.session.commit()
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
