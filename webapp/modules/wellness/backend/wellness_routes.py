"""Wellness API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.storage import BTeamStorage

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
        wellness_data = storage.get_wellness(athlete_id, days_back=days_back)
    else:
        # Get all athletes and compile their wellness data
        all_athletes = storage.list_athletes()
        wellness_data = []
        for athlete in all_athletes:
            athlete_wellness = storage.get_wellness(athlete['id'], days_back=days_back)
            wellness_data.extend(athlete_wellness)
        # Sort by date descending
        wellness_data.sort(key=lambda x: x.get('wellness_date', ''), reverse=True)
    return wellness_data



@router.post("/")
async def create_wellness(wellness: WellnessCreate):
    """Create or update a wellness entry"""
    try:
        result = storage.add_wellness(
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
        if result:
            # Retrieve the created/updated wellness data
            wellness_data = storage.get_wellness(wellness.athlete_id, days_back=30)
            # Find the entry we just created
            for entry in wellness_data:
                if entry.get('wellness_date') == wellness.wellness_date:
                    return entry
            return {"message": "Wellness entry created/updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to create wellness entry")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/athlete/{athlete_id}/latest")
async def get_latest_wellness(athlete_id: int):
    """Get the latest wellness entry for an athlete"""
    wellness_data = storage.get_wellness(athlete_id, days_back=7)
    if not wellness_data:
        raise HTTPException(status_code=404, detail="No wellness data found")
    
    # Return the most recent entry
    return wellness_data[0]
