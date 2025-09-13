from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Literal
from enum import Enum

# Type definitions
Severity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
Status = Literal["OPEN", "INVESTIGATING", "RESOLVED", "CLOSED"]

class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class IncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Incident schemas
class IncidentCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    severity: Severity = "MEDIUM"
    incident_type: Optional[str] = None
    source_ip: Optional[str] = None
    target_system: Optional[str] = None
    # status, detected_at m.m. sätts i backend

class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus

class IncidentOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: IncidentStatus  # Använder enum för kompatibilitet med databas
    severity: IncidentSeverity  # Använder enum för kompatibilitet med databas
    incident_type: Optional[str]
    source_ip: Optional[str]
    target_system: Optional[str]
    detected_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  # pydantic v2

# Backward compatibility alias
Incident = IncidentOut

# System Log schemas
class SystemLogBase(BaseModel):
    log_level: str
    message: str
    source: Optional[str] = None
    metadata: Optional[str] = None

class SystemLogCreate(SystemLogBase):
    pass

class SystemLog(SystemLogBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Log Analysis schemas
class LogAnalysis(BaseModel):
    headline: Optional[str] = None
    top_frame: Optional[str] = None

class LogUploadResponse(BaseModel):
    filename: str
    analysis: LogAnalysis
    message: str
