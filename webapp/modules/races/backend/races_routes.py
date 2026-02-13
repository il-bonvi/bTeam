"""Races API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from storage_bteam import BTeamStorage

router = APIRouter()

storage_dir = Path(__file__).parent.parent.parent / "data"
storage = BTeamStorage(storage_dir)


class RaceCreate(BaseModel):
    name: str
    race_date: str
    distance_km: float
    gender: Optional[str] = None
    category: Optional[str] = None
    elevation_m: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    notes: Optional[str] = None


class RaceAthleteAdd(BaseModel):
    athlete_id: int
    kj_per_hour_per_kg: float = 10.0
    objective: str = "C"


@router.get("/")
async def get_races():
    """Get all races"""
    races = storage.get_all_races()
    return races


@router.get("/{race_id}")
async def get_race(race_id: int):
    """Get a specific race by ID"""
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race


@router.post("/")
async def create_race(race: RaceCreate):
    """Create a new race"""
    try:
        new_race = storage.add_race(
            name=race.name,
            race_date=race.race_date,
            distance_km=race.distance_km,
            gender=race.gender,
            category=race.category,
            elevation_m=race.elevation_m,
            avg_speed_kmh=race.avg_speed_kmh,
            notes=race.notes
        )
        return new_race
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{race_id}")
async def delete_race(race_id: int):
    """Delete a race"""
    existing_race = storage.get_race(race_id)
    if not existing_race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        storage.delete_race(race_id)
        return {"message": "Race deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{race_id}/athletes")
async def add_athlete_to_race(race_id: int, athlete_data: RaceAthleteAdd):
    """Add an athlete to a race"""
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    athlete = storage.get_athlete(athlete_data.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    try:
        storage.add_athlete_to_race(
            race_id=race_id,
            athlete_id=athlete_data.athlete_id,
            kj_per_hour_per_kg=athlete_data.kj_per_hour_per_kg,
            objective=athlete_data.objective
        )
        return {"message": "Athlete added to race successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{race_id}/athletes/{athlete_id}")
async def remove_athlete_from_race(race_id: int, athlete_id: int):
    """Remove an athlete from a race"""
    try:
        storage.remove_athlete_from_race(race_id, athlete_id)
        return {"message": "Athlete removed from race successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{race_id}/athletes")
async def get_race_athletes(race_id: int):
    """Get all athletes for a race"""
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    return race.get('athletes', [])
