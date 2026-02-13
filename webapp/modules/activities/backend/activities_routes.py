"""Activities API Routes"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from storage_bteam import BTeamStorage

router = APIRouter()

storage_dir = Path(__file__).parent.parent.parent / "data"
storage = BTeamStorage(storage_dir)


class ActivityCreate(BaseModel):
    athlete_id: int
    title: str
    activity_date: str
    activity_type: Optional[str] = None
    duration_minutes: Optional[float] = None
    distance_km: Optional[float] = None
    tss: Optional[float] = None
    source: Optional[str] = None
    is_race: bool = False
    avg_watts: Optional[float] = None
    normalized_watts: Optional[float] = None
    avg_hr: Optional[float] = None
    max_hr: Optional[float] = None
    training_load: Optional[float] = None
    intensity: Optional[float] = None
    feel: Optional[int] = None


@router.get("/")
async def get_activities(
    athlete_id: Optional[int] = None,
    limit: Optional[int] = Query(100, le=1000),
    is_race: Optional[bool] = None
):
    """Get all activities with optional filters"""
    activities = storage.list_activities()
    
    if athlete_id:
        activities = [a for a in activities if a['athlete_id'] == athlete_id]
    
    if is_race is not None:
        activities = [a for a in activities if a.get('is_race') == is_race]
    
    return activities[:limit]


@router.get("/{activity_id}")
async def get_activity(activity_id: int):
    """Get a specific activity by ID"""
    activity = storage.get_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.post("/")
async def create_activity(activity: ActivityCreate):
    """Create a new activity"""
    try:
        activity_id = storage.add_activity(
            athlete_id=activity.athlete_id,
            title=activity.title,
            activity_date=activity.activity_date,
            activity_type=activity.activity_type,
            duration_minutes=activity.duration_minutes,
            distance_km=activity.distance_km,
            tss=activity.tss,
            source=activity.source,
            is_race=activity.is_race,
            avg_watts=activity.avg_watts,
            normalized_watts=activity.normalized_watts,
            avg_hr=activity.avg_hr,
            max_hr=activity.max_hr,
            training_load=activity.training_load,
            intensity=activity.intensity,
            feel=activity.feel
        )
        # Retrieve the created activity
        new_activity = storage.get_activity(activity_id)
        return new_activity
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{activity_id}")
async def delete_activity(activity_id: int):
    """Delete an activity"""
    existing_activity = storage.get_activity(activity_id)
    if not existing_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    try:
        storage.delete_activity(activity_id)
        return {"message": "Activity deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/athlete/{athlete_id}/stats")
async def get_athlete_stats(athlete_id: int):
    """Get statistics for an athlete's activities"""
    activities = storage.list_activities()
    athlete_activities = [a for a in activities if a['athlete_id'] == athlete_id]
    
    if not athlete_activities:
        return {
            "total_activities": 0,
            "total_distance_km": 0,
            "total_duration_hours": 0,
            "avg_tss": 0
        }
    
    total_distance = sum(a.get('distance_km', 0) or 0 for a in athlete_activities)
    total_duration = sum(a.get('duration_minutes', 0) or 0 for a in athlete_activities)
    tss_values = [a.get('tss', 0) or 0 for a in athlete_activities if a.get('tss')]
    avg_tss = sum(tss_values) / len(tss_values) if tss_values else 0
    
    return {
        "total_activities": len(athlete_activities),
        "total_distance_km": round(total_distance, 2),
        "total_duration_hours": round(total_duration / 60, 2),
        "avg_tss": round(avg_tss, 2)
    }
