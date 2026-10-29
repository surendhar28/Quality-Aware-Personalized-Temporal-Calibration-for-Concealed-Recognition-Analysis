"""
GazeGuard AI - FastAPI Application Entrypoint.
Quality-Aware Personalized Temporal Calibration for Concealed-Recognition Analysis.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as api_router
from .database.db import init_db

app = FastAPI(
    title="GazeGuard AI - Research API",
    description=(
        "Quality-Aware Personalized Temporal Calibration (QPTC) for Concealed-Recognition Analysis. "
        "Investigates fixation duration patterns, quality-based abstention, and baseline calibration."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Vite frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)


@app.on_event("startup")
def on_startup():
    """Initializes SQLite database tables and verifies directories on startup."""
    init_db()


@app.get("/")
def root():
    return {
        "project": "GazeGuard AI",
        "description": "Quality-Aware Personalized Temporal Calibration for Concealed-Recognition Analysis",
        "version": "1.0.0",
        "api_docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
