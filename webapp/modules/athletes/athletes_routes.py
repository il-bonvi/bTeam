"""Athletes API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from pathlib import Path
import sys
import logging

from shared.storage import get_storage

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()


class AthleteCreate(BaseModel):
    first_name: str
    last_name: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    team_id: Optional[int] = None
    category_id: Optional[int] = None
    kj_per_hour_per_kg: Optional[float] = None
    api_key: Optional[str] = None


class AthleteUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    team_id: Optional[int] = None
    category_id: Optional[int] = None
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
async def get_athletes(team_id: Optional[int] = None, category_id: Optional[int] = None):
    """Get all athletes, optionally filtered by team or category"""
    athletes = get_storage().list_athletes()
    if team_id:
        athletes = [a for a in athletes if a.get('team_id') == team_id]
    if category_id:
        athletes = [a for a in athletes if a.get('category_id') == category_id]
    return athletes


@router.post("/")
async def create_athlete(athlete: AthleteCreate):
    """Create a new athlete"""
    try:
        storage = get_storage()
        athlete_id = storage.add_athlete(
            first_name=athlete.first_name,
            last_name=athlete.last_name,
            birth_date=athlete.birth_date or "",
            gender=athlete.gender,
            team_id=athlete.team_id,
            category_id=athlete.category_id,
            kj_per_hour_per_kg=athlete.kj_per_hour_per_kg,
            api_key=athlete.api_key
        )
        return storage.get_athlete(athlete_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# IMPORTANT: Specific routes must come BEFORE generic routes with path parameters!

@router.get("/{athlete_id}/power-curve")
async def get_athlete_power_curve(
    athlete_id: int,
    oldest: Optional[str] = None,
    newest: Optional[str] = None
):
    """Get power curve data from Intervals.icu for a specific athlete"""
    storage = get_storage()
    athlete = storage.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    if not athlete.get('api_key'):
        raise HTTPException(status_code=400, detail="API key not configured for this athlete")

    try:
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
        if str(root_dir) not in sys.path:
            sys.path.insert(0, str(root_dir))

        from shared.intervals.client import IntervalsAPIClient

        client = IntervalsAPIClient(api_key=athlete['api_key'])

        params = {'type': 'Ride'}
        if oldest:
            if not newest:
                newest = date.today().strftime('%Y-%m-%d')
            params['curves'] = f"r.{oldest}.{newest}"

        response = client._request(
            'GET',
            '/api/v1/athlete/0/power-curves.json',
            params=params
        )
        payload = response.json()

        curves = payload.get('list', []) if isinstance(payload, dict) else []
        if not curves:
            return {'secs': [], 'watts': []}

        first_curve = curves[0]
        return {
            'secs': first_curve.get('secs', []),
            'watts': first_curve.get('values', [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching power curve: {str(e)}")


@router.get("/{athlete_id}")
async def get_athlete(athlete_id: int):
    """Get a specific athlete by ID"""
    athlete = get_storage().get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


@router.put("/{athlete_id}")
async def update_athlete(athlete_id: int, athlete: AthleteUpdate):
    """Update an existing athlete"""
    storage = get_storage()
    if not storage.get_athlete(athlete_id):
        raise HTTPException(status_code=404, detail="Athlete not found")

    try:
        update_data = {k: v for k, v in athlete.dict().items() if v is not None}
        storage.update_athlete(athlete_id, **update_data)
        return storage.get_athlete(athlete_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{athlete_id}")
async def delete_athlete(athlete_id: int):
    """Delete an athlete"""
    storage = get_storage()
    if not storage.get_athlete(athlete_id):
        raise HTTPException(status_code=404, detail="Athlete not found")

    try:
        storage.delete_athlete(athlete_id)
        return {"message": "Athlete deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
