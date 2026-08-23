from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import Base, engine
from backend.app.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="JobHunter AI MVP")

@app.get("/api/debug")
def debug():
    return {
        "message": "FastAPI is running",
        "routes": [
            getattr(route, "path", str(route))
            for route in app.routes
        ]
    }
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}

from backend.app.routes import auth, profile, jobs, gmail, applications, email, notifications

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(gmail.router)
app.include_router(applications.router)
app.include_router(email.router)
app.include_router(notifications.router)
