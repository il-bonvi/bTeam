"""Seasons API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path

from shared.storage import BTeamStorage

router = APIRouter()

storage_dir = Path(__file__).resolve().parent.parent.parent.parent / "data"
storage = BTeamStorage(storage_dir)


class SeasonCreate(BaseModel):
    name: str
    start_date: str  # YYYY-MM-DD


class SeasonUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[str] = None


@router.get("/{athlete_id}/seasons")
async def get_athlete_seasons(athlete_id: int):
    """Get all seasons for an athlete"""
    athlete = storage.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    seasons = storage.get_seasons(athlete_id)
    return seasons


@router.post("/{athlete_id}/seasons")
async def create_season(athlete_id: int, season: SeasonCreate):
    """Create a new season for an athlete"""
    athlete = storage.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    try:
        new_season = storage.create_season(
            athlete_id=athlete_id,
            name=season.name,
            start_date=season.start_date
        )
        return new_season
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/seasons/{season_id}")
async def get_season(season_id: int):
    """Get a specific season"""
    season = storage.get_season(season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    return season


@router.put("/seasons/{season_id}")
async def update_season(season_id: int, season: SeasonUpdate):
    """Update a season"""
    existing = storage.get_season(season_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Season not found")
    
    try:
        update_data = {k: v for k, v in season.dict().items() if v is not None}
        storage.update_season(season_id, **update_data)
        return storage.get_season(season_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/seasons/{season_id}")
async def delete_season(season_id: int):
    """Delete a season"""
    existing = storage.get_season(season_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Season not found")
    
    try:
        storage.delete_season(season_id)
        return {"message": "Season deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
