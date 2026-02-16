"""Athletes API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date, timedelta
from pathlib import Path
import sys
import os
import logging

from shared.storage import BTeamStorage

# Setup logging
logger = logging.getLogger(__name__)

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
    birth_date: Optional[str] = None
    gender: Optional[str] = None
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


# IMPORTANT: Specific routes must come BEFORE generic routes with path parameters!
# This route must be before GET /{athlete_id} so it doesn't get matched as athlete_id="1/power-curve"

@router.get("/{athlete_id}/power-curve")
async def get_athlete_power_curve(
    athlete_id: int,
    oldest: Optional[str] = None,
    newest: Optional[str] = None
):
    """Get power curve data from Intervals.icu for a specific athlete"""
    athlete = storage.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    if not athlete.get('api_key'):
        raise HTTPException(status_code=400, detail="API key not configured for this athlete")

    try:
        # Ensure shared module is importable
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
        if str(root_dir) not in sys.path:
            sys.path.insert(0, str(root_dir))

        from shared.intervals.client import IntervalsAPIClient

        client = IntervalsAPIClient(api_key=athlete['api_key'])

        # Intervals.icu uses /power-curves{ext} for athlete curves
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
        secs = first_curve.get('secs', [])
        watts = first_curve.get('values', [])

        return {'secs': secs, 'watts': watts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching power curve: {str(e)}")


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


@router.get("/{athlete_id}")
async def get_athlete(athlete_id: int):
    """Get a specific athlete by ID"""
    athlete = storage.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


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
