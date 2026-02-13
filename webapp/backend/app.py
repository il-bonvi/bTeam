#!/usr/bin/env python3
"""
bTeam WebApp - Main Backend Application
FastAPI-based REST API for cycling team management
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
import sys
from pathlib import Path

# Add parent directory to path to import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from storage_bteam import BTeamStorage
from intervals_client_v2 import IntervalsAPIClient
from intervals_sync import IntervalsSyncService

# Initialize FastAPI app
app = FastAPI(
    title="bTeam API",
    description="REST API for cycling team management and Intervals.icu integration",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Initialize storage
storage_dir = Path(__file__).parent.parent / "data"
storage_dir.mkdir(exist_ok=True)
storage = BTeamStorage(storage_dir)


def get_db():
    """Dependency for database session"""
    return storage.session


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application page"""
    html_file = Path(__file__).parent.parent / "templates" / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return HTMLResponse("<h1>bTeam WebApp</h1><p>Welcome to the cycling team management system</p>")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "bTeam API is running"}


# Import route modules
from modules.teams.backend import teams_routes
from modules.athletes.backend import athletes_routes
from modules.activities.backend import activities_routes
from modules.races.backend import races_routes
from modules.wellness.backend import wellness_routes
from modules.sync.backend import sync_routes

# Include routers
app.include_router(teams_routes.router, prefix="/api/teams", tags=["Teams"])
app.include_router(athletes_routes.router, prefix="/api/athletes", tags=["Athletes"])
app.include_router(activities_routes.router, prefix="/api/activities", tags=["Activities"])
app.include_router(races_routes.router, prefix="/api/races", tags=["Races"])
app.include_router(wellness_routes.router, prefix="/api/wellness", tags=["Wellness"])
app.include_router(sync_routes.router, prefix="/api/sync", tags=["Synchronization"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
