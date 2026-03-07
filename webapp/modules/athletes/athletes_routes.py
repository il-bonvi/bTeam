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
    custom_cp_configs: Optional[dict] = None


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


# Custom CP Configuration (MUST come before /{athlete_id} DELETE)

class CustomCPConfig(BaseModel):
    selected_durations: list  # List of seconds
    cp: float
    w_prime: float
    pmax: float
    period: str  # '90d', 'allTime', 'season-X', etc
    period_label: Optional[str] = None  # Human-readable label
    date_start: Optional[str] = None  # ISO date start (YYYY-MM-DD)
    date_end: Optional[str] = None  # ISO date end (YYYY-MM-DD)
    rmse: Optional[float] = None


@router.post("/{athlete_id}/custom-cp")
async def save_custom_cp_config(athlete_id: int, config: CustomCPConfig):
    """Save custom CP configuration for an athlete (creates new historical record)"""
    storage = get_storage()
    athlete = storage.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    try:
        # Use provided dates or period_label as the identifier
        display_label = config.period_label
        if config.date_start and config.date_end and config.date_start != config.date_end:
            # Format as "YYYY-MM-DD - YYYY-MM-DD"
            display_label = f"{config.date_start} - {config.date_end}"
        
        # Save to history (does NOT overwrite, creates new record)
        saved_config = storage.save_custom_cp(
            athlete_id=athlete_id,
            period=config.period,
            period_label=display_label,
            selected_durations=config.selected_durations,
            cp=config.cp,
            w_prime=config.w_prime,
            pmax=config.pmax,
            rmse=config.rmse
        )
        return {
            "message": "Custom CP configuration saved",
            "id": saved_config["id"],
            "saved_at": saved_config["saved_at"]
        }
    except Exception as e:
        logger.error(f"Error saving custom CP config: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{athlete_id}/custom-cp-history")
async def get_custom_cp_history(
    athlete_id: int,
    period: Optional[str] = None,
    limit: int = 50
):
    """Get Custom CP configuration history for an athlete"""
    storage = get_storage()
    athlete = storage.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    history = storage.get_custom_cp_history(athlete_id, period=period, limit=limit)
    return history


@router.get("/{athlete_id}/custom-cp/latest/{period}")
async def get_latest_custom_cp(athlete_id: int, period: str):
    """Get the most recent Custom CP configuration for a specific period"""
    storage = get_storage()
    athlete = storage.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    config = storage.get_latest_custom_cp(athlete_id, period)
    if not config:
        raise HTTPException(status_code=404, detail="No custom CP config found for this period")
    
    return config


@router.get("/{athlete_id}/custom-cp-detail/{config_id}")
async def get_custom_cp_by_id(athlete_id: int, config_id: int):
    """Get a specific Custom CP configuration by ID"""
    storage = get_storage()
    config = storage.get_custom_cp_by_id(config_id)
    if not config or config["athlete_id"] != athlete_id:
        raise HTTPException(status_code=404, detail="Custom CP config not found")
    
    return config


@router.delete("/{athlete_id}/custom-cp-history/{config_id}")
async def delete_custom_cp_config(athlete_id: int, config_id: int):
    """Delete a Custom CP configuration from history"""
    storage = get_storage()
    config = storage.get_custom_cp_by_id(config_id)
    if not config or config["athlete_id"] != athlete_id:
        raise HTTPException(status_code=404, detail="Custom CP config not found")
    
    try:
        if storage.delete_custom_cp(config_id):
            return {"message": "Custom CP configuration deleted"}
        else:
            raise HTTPException(status_code=404, detail="Config not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Legacy endpoints (kept for backwards compatibility - now deprecated)

@router.get("/{athlete_id}/custom-cp/{period}")
async def get_custom_cp_config_legacy(athlete_id: int, period: str):
    """
    DEPRECATED: Get custom CP configuration for an athlete and period.
    Use /custom-cp/latest/{period} instead.
    Returns the most recent configuration for backwards compatibility.
    """
    storage = get_storage()
    athlete = storage.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    config = storage.get_latest_custom_cp(athlete_id, period)
    if not config:
        # Fall back to old custom_cp_configs field for backwards compatibility
        custom_configs = athlete.get('custom_cp_configs', {})
        if period not in custom_configs:
            raise HTTPException(status_code=404, detail="No custom CP config for this period")
        return custom_configs[period]
    
    return config


@router.delete("/{athlete_id}/custom-cp/{period}")
async def delete_custom_cp_config_legacy(athlete_id: int, period: str):
    """
    DEPRECATED: Delete custom CP configuration for an athlete and period.
    This now deletes ALL history for this period.
    """
    storage = get_storage()
    athlete = storage.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    # Get all configs for this period and delete them
    history = storage.get_custom_cp_history(athlete_id, period=period)
    deleted_count = 0
    for config in history:
        if storage.delete_custom_cp(config["id"]):
            deleted_count += 1
    
    return {"message": f"Deleted {deleted_count} custom CP configuration(s)"}


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
