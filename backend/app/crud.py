from sqlalchemy.orm import Session
from sqlalchemy import desc
from app import models, schemas
from passlib.context import CryptContext
from datetime import datetime

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Incident CRUD operations
def get_incident(db: Session, incident_id: int):
    return db.query(models.Incident).filter(models.Incident.id == incident_id).first()

def get_incidents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Incident).order_by(desc(models.Incident.created_at)).offset(skip).limit(limit).all()

def list_incidents(db: Session, limit: int = 50):
    return (
        db.query(models.Incident)
        .order_by(models.Incident.created_at.desc())
        .limit(limit)
        .all()
    )

def create_incident(db: Session, incident: schemas.IncidentCreate):
    db_incident = models.Incident(
        title=incident.title,
        description=incident.description,
        status="OPEN",                   # default
        severity=incident.severity,
        incident_type=incident.incident_type,
        source_ip=incident.source_ip,
        target_system=incident.target_system,
        detected_at=datetime.utcnow(),   # sätts nu
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

def update_incident_status(db: Session, incident_id: int, status: str):
    db_incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if db_incident:
        db_incident.status = status
        if status in ["resolved", "closed"]:
            db_incident.resolved_at = datetime.now()
        db.commit()
        db.refresh(db_incident)
    return db_incident

# System Log CRUD operations
def create_system_log(db: Session, log: schemas.SystemLogCreate):
    db_log = models.SystemLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_system_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SystemLog).order_by(desc(models.SystemLog.timestamp)).offset(skip).limit(limit).all()
