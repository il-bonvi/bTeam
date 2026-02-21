#!/usr/bin/env python3
"""
bTeam WebApp - Main Backend Application
FastAPI-based REST API for cycling team management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add webapp directory to sys.path so that 'shared' and 'modules' sono trovati
webapp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, webapp_dir)

from shared.storage import BTeamStorage

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

# Mount modules directory to serve frontend assets (JS, CSS) from each module
modules_path = Path(__file__).parent.parent / "modules"
app.mount("/modules", StaticFiles(directory=str(modules_path)), name="modules")

# Initialize storage
storage_dir = Path(__file__).parent.parent / "data"
storage_dir.mkdir(exist_ok=True)
storage = BTeamStorage(storage_dir)
logger.info(f"[bTeam] Storage initialized at {storage_dir}")


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


@app.get("/debug/test")
async def debug_test():
    """Test endpoint for debugging"""
    return {"status": "ok", "message": "Test endpoint works"}


# Import route modules
from modules.teams import teams_routes
from modules.categories import categories_routes
from modules.athletes import athletes_routes, seasons_routes
from modules.activities import activities_routes
from modules.races import races_routes
from modules.wellness import wellness_routes
from modules.sync import sync_routes

# Include routers
app.include_router(teams_routes.router, prefix="/api/teams", tags=["Teams"])
app.include_router(categories_routes.router, prefix="/api/categories", tags=["Categories"])
app.include_router(athletes_routes.router, prefix="/api/athletes", tags=["Athletes"])
app.include_router(seasons_routes.router, prefix="/api/athletes", tags=["Seasons"])
app.include_router(activities_routes.router, prefix="/api/activities", tags=["Activities"])
app.include_router(races_routes.router, prefix="/api/races", tags=["Races"])
app.include_router(wellness_routes.router, prefix="/api/wellness", tags=["Wellness"])
app.include_router(sync_routes.router, prefix="/api/sync", tags=["Synchronization"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
