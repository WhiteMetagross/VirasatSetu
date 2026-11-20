import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.database import engine, Base
from app.seed.sample_data import seed_all
from app.middleware.security_middleware import (
    SecurityHeadersMiddleware,
    CSRFProtectionMiddleware,
    RateLimitingMiddleware
)

# Routers
from app.routers import (
    auth,
    deceased,
    matching,
    claimants,
    claims,
    notifications,
    admin,
    institutions,
    documents,
    dashboard,
    ai
)

# Initialize tables and verify seed data
Base.metadata.create_all(bind=engine)
try:
    seed_all()
except Exception as err:
    print(f"Startup initialization notice: {err}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Digital Inheritance & Unclaimed Financial Asset Discovery Platform Prototype",
    version="1.0.0"
)

# CORS configuration
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cybersecurity Defenses: Security Headers, CSRF Protection, and Rate Limiting
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFProtectionMiddleware)
app.add_middleware(RateLimitingMiddleware)

# Register API Routers
app.include_router(auth.router)
app.include_router(deceased.router)
app.include_router(matching.router)
app.include_router(claimants.router)
app.include_router(claims.router)
app.include_router(notifications.router)
app.include_router(admin.router)
app.include_router(institutions.router)
app.include_router(documents.router)
app.include_router(dashboard.router)
app.include_router(ai.router)

# Mount static folder
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
def on_startup():
    # Automatically seed sample data if not already present
    seed_all()

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Virasat Setu API is running. Access API docs at /docs"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": "1.0.0"}
