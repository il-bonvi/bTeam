"""Wellness API Routes"""

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


class WellnessCreate(BaseModel):
    athlete_id: int
    wellness_date: str
    weight_kg: Optional[float] = None
    resting_hr: Optional[int] = None
    hrv: Optional[float] = None
    steps: Optional[int] = None
    soreness: Optional[int] = None
    fatigue: Optional[int] = None
    stress: Optional[int] = None
    mood: Optional[int] = None
    motivation: Optional[int] = None
    sleep_secs: Optional[int] = None
    sleep_score: Optional[int] = None
    comments: Optional[str] = None


@router.get("/")
async def get_wellness(athlete_id: Optional[int] = None, days_back: int = 30):
    """Get wellness data, optionally filtered by athlete"""
    if athlete_id:
        wellness_data = storage.get_wellness_by_athlete(athlete_id, days_back=days_back)
    else:
        wellness_data = storage.get_all_wellness(days_back=days_back)
    return wellness_data


@router.get("/{wellness_id}")
async def get_wellness_entry(wellness_id: int):
    """Get a specific wellness entry by ID"""
    wellness = storage.get_wellness_entry(wellness_id)
    if not wellness:
        raise HTTPException(status_code=404, detail="Wellness entry not found")
    return wellness


@router.post("/")
async def create_wellness(wellness: WellnessCreate):
    """Create a new wellness entry"""
    try:
        new_wellness = storage.add_wellness(
            athlete_id=wellness.athlete_id,
            wellness_date=wellness.wellness_date,
            weight_kg=wellness.weight_kg,
            resting_hr=wellness.resting_hr,
            hrv=wellness.hrv,
            steps=wellness.steps,
            soreness=wellness.soreness,
            fatigue=wellness.fatigue,
            stress=wellness.stress,
            mood=wellness.mood,
            motivation=wellness.motivation,
            sleep_secs=wellness.sleep_secs,
            sleep_score=wellness.sleep_score,
            comments=wellness.comments
        )
        return new_wellness
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{wellness_id}")
async def update_wellness(wellness_id: int, wellness: WellnessCreate):
    """Update an existing wellness entry"""
    existing_wellness = storage.get_wellness_entry(wellness_id)
    if not existing_wellness:
        raise HTTPException(status_code=404, detail="Wellness entry not found")
    
    try:
        update_data = {k: v for k, v in wellness.dict().items() if v is not None and k != 'athlete_id'}
        updated_wellness = storage.update_wellness(wellness_id, **update_data)
        return updated_wellness
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{wellness_id}")
async def delete_wellness(wellness_id: int):
    """Delete a wellness entry"""
    existing_wellness = storage.get_wellness_entry(wellness_id)
    if not existing_wellness:
        raise HTTPException(status_code=404, detail="Wellness entry not found")
    
    try:
        storage.delete_wellness(wellness_id)
        return {"message": "Wellness entry deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/athlete/{athlete_id}/latest")
async def get_latest_wellness(athlete_id: int):
    """Get the latest wellness entry for an athlete"""
    wellness_data = storage.get_wellness_by_athlete(athlete_id, days_back=7)
    if not wellness_data:
        raise HTTPException(status_code=404, detail="No wellness data found")
    
    # Return the most recent entry
    return wellness_data[0]
