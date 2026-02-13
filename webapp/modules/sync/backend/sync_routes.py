"""Intervals.icu Sync API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from intervals_sync import IntervalsSyncService
from intervals_client_v2 import IntervalsAPIClient
from storage_bteam import BTeamStorage

router = APIRouter()

storage_dir = Path(__file__).parent.parent.parent / "data"
storage = BTeamStorage(storage_dir)


class APIKeyRequest(BaseModel):
    api_key: str


class SyncRequest(BaseModel):
    athlete_id: int
    api_key: str
    days_back: int = 30
    include_intervals: bool = True


class WellnessSyncRequest(BaseModel):
    athlete_id: int
    api_key: str
    days_back: int = 7


class PushRaceRequest(BaseModel):
    race_id: int
    api_key: str


@router.post("/test-connection")
async def test_connection(request: APIKeyRequest):
    """Test connection to Intervals.icu"""
    try:
        sync_service = IntervalsSyncService(api_key=request.api_key)
        if sync_service.is_connected():
            athlete_data = sync_service.client.get_athlete()
            return {
                "success": True,
                "message": "Connection successful",
                "athlete_name": f"{athlete_data.get('name', 'Unknown')}"
            }
        else:
            raise HTTPException(status_code=401, detail="Connection failed")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Connection failed: {str(e)}")


@router.post("/activities")
async def sync_activities(request: SyncRequest):
    """Sync activities from Intervals.icu"""
    try:
        sync_service = IntervalsSyncService(api_key=request.api_key)
        
        if not sync_service.is_connected():
            raise HTTPException(status_code=401, detail="Not connected to Intervals.icu")
        
        activities, message = sync_service.fetch_activities(
            days_back=request.days_back,
            include_intervals=request.include_intervals
        )
        
        if not activities:
            return {"success": True, "message": message, "imported": 0}
        
        # Import activities into database
        imported_count = 0
        for activity in activities:
            try:
                formatted = IntervalsSyncService.format_activity_for_storage(activity)
                storage.add_activity(
                    athlete_id=request.athlete_id,
                    title=formatted['name'],
                    activity_date=formatted['start_date'],
                    activity_type=formatted.get('type'),
                    duration_minutes=formatted.get('moving_time_minutes'),
                    distance_km=formatted.get('distance_km'),
                    tss=formatted.get('training_load'),
                    source='INTERVALS',
                    avg_watts=formatted.get('avg_watts'),
                    normalized_watts=formatted.get('normalized_watts'),
                    avg_hr=formatted.get('avg_hr'),
                    max_hr=formatted.get('max_hr'),
                    training_load=formatted.get('training_load'),
                    intensity=formatted.get('intensity'),
                    feel=formatted.get('feel')
                )
                imported_count += 1
            except Exception as e:
                print(f"Error importing activity: {e}")
                continue
        
        return {
            "success": True,
            "message": f"Imported {imported_count} activities",
            "imported": imported_count,
            "total": len(activities)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/wellness")
async def sync_wellness(request: WellnessSyncRequest):
    """Sync wellness data from Intervals.icu"""
    try:
        sync_service = IntervalsSyncService(api_key=request.api_key)
        
        if not sync_service.is_connected():
            raise HTTPException(status_code=401, detail="Not connected to Intervals.icu")
        
        wellness_data = sync_service.client.get_wellness(days_back=request.days_back)
        
        if not wellness_data:
            return {"success": True, "message": "No wellness data found", "imported": 0}
        
        # Import wellness data
        imported_count = 0
        for entry in wellness_data:
            try:
                storage.add_wellness(
                    athlete_id=request.athlete_id,
                    wellness_date=entry.get('id'),
                    weight_kg=entry.get('weight'),
                    resting_hr=entry.get('restingHR'),
                    hrv=entry.get('hrv'),
                    steps=entry.get('steps'),
                    soreness=entry.get('soreness'),
                    fatigue=entry.get('fatigue'),
                    stress=entry.get('mentalReadiness'),
                    mood=entry.get('mood'),
                    motivation=entry.get('motivation'),
                    sleep_secs=entry.get('sleepSecs'),
                    sleep_score=entry.get('sleepScore'),
                    comments=entry.get('comments')
                )
                imported_count += 1
            except Exception as e:
                print(f"Error importing wellness: {e}")
                continue
        
        return {
            "success": True,
            "message": f"Imported {imported_count} wellness entries",
            "imported": imported_count
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/push-race")
async def push_race(request: PushRaceRequest):
    """Push a race to Intervals.icu as a planned event"""
    try:
        race = storage.get_race(request.race_id)
        if not race:
            raise HTTPException(status_code=404, detail="Race not found")
        
        client = IntervalsAPIClient(api_key=request.api_key)
        
        # Create event on Intervals.icu
        event_data = {
            "category": "RACE",
            "start_date_local": f"{race['race_date']}T10:00:00",
            "name": race['name'],
            "type": "Ride",
            "description": f"Distance: {race['distance_km']}km\nCategory: {race.get('category', 'N/A')}",
        }
        
        result = client.create_event(**event_data)
        
        return {
            "success": True,
            "message": "Race pushed to Intervals.icu successfully",
            "event_id": result.get('id')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/power-curve/{athlete_id}")
async def get_power_curve(athlete_id: int, api_key: str, days_back: int = 90):
    """Get power curve data from Intervals.icu"""
    try:
        client = IntervalsAPIClient(api_key=api_key)
        # Calculate dates for oldest/newest parameters based on days_back
        from datetime import datetime, timedelta
        newest = datetime.now().strftime('%Y-%m-%d')
        oldest = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        power_curve = client.get_power_curve(athlete_id=str(athlete_id), oldest=oldest, newest=newest)
        
        return {
            "success": True,
            "data": power_curve
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
