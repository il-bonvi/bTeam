"""Athletes API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path

from shared.storage import BTeamStorage

router = APIRouter()

storage_dir = Path(__file__).resolve().parent.parent.parent.parent / "data"
storage = BTeamStorage(storage_dir)


class AthleteCreate(BaseModel):
    first_name: str
    last_name: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    team_id: Optional[int] = None
    kj_per_hour_per_kg: Optional[float] = None
    api_key: Optional[str] = None


class AthleteUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    team_id: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    cp: Optional[float] = None
    max_hr: Optional[float] = None
    w_prime: Optional[float] = None
    ecp: Optional[float] = None
    ew_prime: Optional[float] = None
    kj_per_hour_per_kg: Optional[float] = None
    api_key: Optional[str] = None


@router.get("/")
async def get_athletes(team_id: Optional[int] = None):
    """Get all athletes, optionally filtered by team"""
    athletes = storage.list_athletes()
    if team_id:
        athletes = [a for a in athletes if a.get('team_id') == team_id]
    return athletes


@router.get("/{athlete_id}")
async def get_athlete(athlete_id: int):
    """Get a specific athlete by ID"""
    athlete = storage.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


@router.post("/")
async def create_athlete(athlete: AthleteCreate):
    """Create a new athlete"""
    try:
        athlete_id = storage.add_athlete(
            first_name=athlete.first_name,
            last_name=athlete.last_name,
            birth_date=athlete.birth_date or "",
            gender=athlete.gender,
            team_id=athlete.team_id,
            kj_per_hour_per_kg=athlete.kj_per_hour_per_kg,
            api_key=athlete.api_key
        )
        # Retrieve the created athlete
        new_athlete = storage.get_athlete(athlete_id)
        return new_athlete
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{athlete_id}")
async def update_athlete(athlete_id: int, athlete: AthleteUpdate):
    """Update an existing athlete"""
    existing_athlete = storage.get_athlete(athlete_id)
    if not existing_athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    try:
        update_data = {k: v for k, v in athlete.dict().items() if v is not None}
        storage.update_athlete(athlete_id, **update_data)
        # Return updated athlete
        updated_athlete = storage.get_athlete(athlete_id)
        return updated_athlete
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{athlete_id}")
async def delete_athlete(athlete_id: int):
    """Delete an athlete"""
    existing_athlete = storage.get_athlete(athlete_id)
    if not existing_athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    try:
        storage.delete_athlete(athlete_id)
        return {"message": "Athlete deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
