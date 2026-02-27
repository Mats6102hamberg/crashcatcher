from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import SessionLocal, engine
from app.security import require_api_key
import logging
from datetime import datetime
import jwt
import os
import shutil
import re
import httpx

# Skapa databastabeller
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Security Monitor API", version="1.0.0")

# Upload directory
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# CORS middleware
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def simple_analyze(text: str):
    """Enkel analys av loggtext för att hitta exceptions och stack frames"""
    # Hitta första exception-liknande rad
    m = re.search(r'([A-Za-z_0-9]+Exception|Error).*', text)
    top = m.group(0) if m else None
    # Hitta första stack-frame (fil:linje)
    frame = re.search(r'(\w+\.py:\d+|\w+:\d+)', text)
    frame_str = frame.group(0) if frame else None
    return {"headline": top, "top_frame": frame_str}

@app.get("/")
def read_root():
    return {"message": "Security Monitor API", "status": "running"}

@app.post("/auth/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create JWT token
    token_data = {"sub": user.username}
    token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    
    return {"access_token": token, "token_type": "bearer"}

@app.post("/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/incidents/", response_model=list[schemas.IncidentOut])
def read_incidents(limit: int = 50, 
                  api_key_validated: None = Depends(require_api_key),
                  db: Session = Depends(get_db)):
    incidents = crud.list_incidents(db, limit=limit)
    return incidents

BORIS_WEBHOOK_URL = os.getenv("BORIS_WEBHOOK_URL")
BORIS_API_KEY = os.getenv("BORIS_API_KEY", "")

def forward_to_boris(incident_data: dict):
    """Fire-and-forget: forward incident to Boris Marketing"""
    if not BORIS_WEBHOOK_URL:
        return
    try:
        httpx.post(
            BORIS_WEBHOOK_URL,
            json={"source": "crashcatcher", **incident_data},
            headers={"x-api-key": BORIS_API_KEY, "Content-Type": "application/json"},
            timeout=10,
        )
    except Exception as e:
        logger.error(f"Boris webhook failed: {e}")

@app.post("/incidents/", response_model=schemas.IncidentOut)
def create_incident(incident: schemas.IncidentCreate,
                   api_key_validated: None = Depends(require_api_key),
                   db: Session = Depends(get_db)):
    result = crud.create_incident(db=db, incident=incident)
    forward_to_boris(incident.model_dump())
    return result

# Alternative endpoints without trailing slash
@app.post("/incidents", response_model=schemas.IncidentOut)
def create_incident_alt(inc: schemas.IncidentCreate,
                       _=Depends(require_api_key)):
    db = SessionLocal()
    try:
        result = crud.create_incident(db, inc)
        forward_to_boris(inc.model_dump())
        return result
    finally:
        db.close()

@app.get("/incidents", response_model=list[schemas.IncidentOut])
def get_incidents_alt(limit: int = 50, 
                     _=Depends(require_api_key)):
    db = SessionLocal()
    try:
        return crud.list_incidents(db, limit=limit)
    finally:
        db.close()

@app.get("/incidents/{incident_id}", response_model=schemas.IncidentOut)
def read_incident(incident_id: int,
                 api_key_validated: None = Depends(require_api_key),
                 db: Session = Depends(get_db)):
    db_incident = crud.get_incident(db, incident_id=incident_id)
    if db_incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return db_incident

@app.put("/incidents/{incident_id}/status")
def update_incident_status(incident_id: int, 
                          status_update: schemas.IncidentStatusUpdate,
                          api_key_validated: None = Depends(require_api_key),
                          db: Session = Depends(get_db)):
    db_incident = crud.update_incident_status(db, incident_id, status_update.status)
    if db_incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"message": "Status updated successfully"}

@app.post("/upload-log", response_model=schemas.LogUploadResponse)
async def upload_log(file: UploadFile = File(...), 
                    api_key_validated: None = Depends(require_api_key)):
    """Upload och analysera loggfiler för säkerhetsincidenter"""
    if file.content_type not in ("text/plain", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Endast textfiler tillåtna.")
    
    # Spara filen
    path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Läs och analysera filen
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            txt = fh.read(20000)  # läs max 20k tecken för analys
        
        analysis = simple_analyze(txt)
        
        # Här kan du istället skapa ett 'case' i databasen och returnera case-id
        logger.info(f"Log file uploaded and analyzed: {file.filename}")
        
        return {
            "filename": file.filename, 
            "analysis": analysis,
            "message": "Log file uploaded and analyzed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing log file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Error processing log file")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
