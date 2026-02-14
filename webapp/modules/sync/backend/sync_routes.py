"""Intervals.icu Sync API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.intervals.sync import IntervalsSyncService
from shared.intervals.client import IntervalsAPIClient
from shared.storage import BTeamStorage

router = APIRouter()

storage_dir = Path(__file__).parent.parent.parent.parent / "data"
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
    days_back: int = 30


class PushRaceRequest(BaseModel):
    race_id: int
    athlete_id: int
    api_key: str


@router.post("/test-connection")
async def test_connection(request: APIKeyRequest):
    """Test connection to Intervals.icu"""
    try:
        sync_service = IntervalsSyncService(api_key=request.api_key)
        if sync_service.is_connected():
            assert sync_service.client is not None
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
        skipped_count = 0
        for activity in activities:
            try:
                formatted = IntervalsSyncService.format_activity_for_storage(activity)
                activity_id, is_new = storage.add_activity(
                    athlete_id=request.athlete_id,
                    title=formatted['name'],
                    activity_date=formatted['start_date'],
                    activity_type=formatted.get('type'),
                    duration_minutes=formatted.get('moving_time_minutes'),
                    distance_km=formatted.get('distance_km'),
                    tss=formatted.get('training_load'),
                    source='intervals',
                    intervals_id=formatted.get('intervals_id'),
                    avg_watts=formatted.get('avg_watts'),
                    normalized_watts=formatted.get('normalized_watts'),
                    avg_hr=formatted.get('avg_hr'),
                    max_hr=formatted.get('max_hr'),
                    training_load=formatted.get('training_load'),
                    intensity=formatted.get('intensity'),
                    feel=formatted.get('feel')
                )
                if is_new:
                    imported_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                print(f"Error importing activity: {e}")
                continue
        
        return {
            "success": True,
            "message": f"Imported {imported_count} activities, skipped {skipped_count} duplicates",
            "imported": imported_count,
            "skipped": skipped_count,
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
        
        assert sync_service.client is not None
        wellness_data = sync_service.client.get_wellness(days_back=request.days_back)
        
        if not wellness_data:
            return {"success": True, "message": "No wellness data found", "imported": 0}
        
        # Import wellness data
        imported_count = 0
        for entry in wellness_data:
            try:
                wellness_date = entry.get('id')
                if not wellness_date:
                    continue  # Skip entries without date
                body_fat_value = entry.get('bodyFat')
                storage.add_wellness(
                    athlete_id=request.athlete_id,
                    wellness_date=str(wellness_date),
                    weight_kg=entry.get('weight'),
                    resting_hr=entry.get('restingHR'),
                    hrv=entry.get('hrv'),
                    steps=entry.get('steps'),
                    soreness=entry.get('soreness'),
                    fatigue=entry.get('fatigue'),
                    stress=entry.get('stress'),
                    mood=entry.get('mood'),
                    motivation=entry.get('motivation'),
                    injury=entry.get('injury'),
                    kcal=entry.get('kcalConsumed'),
                    sleep_secs=entry.get('sleepSecs'),
                    sleep_score=entry.get('sleepScore'),
                    sleep_quality=entry.get('sleepQuality'),
                    avg_sleeping_hr=entry.get('avgSleepingHR'),
                    menstruation=None,  # Not directly available in API
                    menstrual_cycle_phase=entry.get('menstrualPhase'),
                    body_fat=body_fat_value,
                    respiration=entry.get('respiration'),
                    spO2=entry.get('spO2'),
                    readiness=entry.get('readiness'),
                    ctl=entry.get('ctl'),
                    atl=entry.get('atl'),
                    ramp_rate=entry.get('rampRate'),
                    comments=entry.get('comments')
                )
                imported_count += 1
            except Exception as e:
                continue
        
        return {
            "success": True,
            "message": f"Imported {imported_count} wellness entries",
            "imported": imported_count,
            "total_found": len(wellness_data)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/push-race")
async def push_race(request: PushRaceRequest):
    """Push a race to Intervals.icu as a planned event (matching OLDAPP implementation)"""
    try:
        race = storage.get_race(request.race_id)
        if not race:
            raise HTTPException(status_code=404, detail="Race not found")
        
        # Get athlete to ensure they exist
        athlete = storage.get_athlete(request.athlete_id)
        if not athlete:
            raise HTTPException(status_code=404, detail="Athlete not found")
        
        client = IntervalsAPIClient(api_key=request.api_key)
        
        # Extract race data with defaults
        distance_km = race.get('distance_km') or 0
        elevation_m = race.get('elevation_m') or 0
        predicted_kj = race.get('predicted_kj') or 0
        category = race.get('category') or 'C'
        notes = race.get('notes') or ''
        
        # Calculate duration from predicted data or estimate
        # If we have predicted_duration_minutes, use that, otherwise estimate 4 hours
        predicted_duration = race.get('predicted_duration_minutes')
        if predicted_duration:
            duration_minutes = float(predicted_duration)
        else:
            # Default estimate: 25 km/h average speed
            duration_minutes = (distance_km / 25.0) * 60 if distance_km > 0 else 240
        
        duration_seconds = int(duration_minutes * 60)
        
        # Calculate end_date_local
        from datetime import datetime, timedelta
        start_date_local = f"{race['race_date']}T10:00:00"
        start_dt = datetime.fromisoformat(start_date_local)
        end_dt = start_dt + timedelta(seconds=duration_seconds)
        end_date_local = end_dt.isoformat()
        
        # Map category to Intervals category (A/B/C → RACE_A/RACE_B/RACE_C)
        category_upper = str(category).upper()
        if category_upper in ['A', 'B', 'C']:
            intervals_category = f"RACE_{category_upper}"
        else:
            intervals_category = "RACE_C"  # Default to C
        
        # Build HTML-formatted description like OLDAPP
        race_description = f'<div><b></b><span class="text-red-darken-2"><b class="">Dislivello</b></span>: {int(elevation_m)}m</div>'
        race_description += f'<div><b></b><span class="text-green"><b class="">Previsti</b></span>: {int(predicted_kj)}kJ</div>'
        if notes:
            race_description += f'<div><b></b><span class="text-purple"><b class="">Note</b></span>: {notes}</div>'
        
        # Create event with ALL parameters from OLDAPP
        # Use "0" for athlete_id (means "current athlete" who owns the API key)
        # In OLDAPP: athlete.get("intervals_id") or "0"
        result = client.create_event(
            athlete_id="0",
            category=intervals_category,
            start_date_local=start_date_local,
            end_date_local=end_date_local,
            name=race['name'],
            description=race_description,
            activity_type='Ride',
            distance=distance_km * 1000,  # Convert km to meters
            moving_time=duration_seconds
        )
        
        return {
            "success": True,
            "message": "Race pushed to Intervals.icu successfully",
            "event_id": result.get('id')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/athlete-metrics")
async def sync_athlete_metrics(athlete_id: int, api_key: str):
    """Sync athlete metrics (weight, FTP, max HR, W', eCP, eW') from Intervals.icu"""
    try:
        client = IntervalsAPIClient(api_key=api_key)
        athlete_data = client.get_athlete()

        sport_settings = athlete_data.get('sportSettings') or []
        cycling_settings = sport_settings[0] if sport_settings else {}
        mmp_model = cycling_settings.get('mmp_model') or {}

        # Height from athlete data (in meters, convert to cm)
        height_cm = None
        if athlete_data.get('height') is not None:
            height_m = athlete_data.get('height')
            if isinstance(height_m, (int, float)) and height_m > 0:
                height_cm = height_m * 100

        # Weight: always try to get from wellness first (most up-to-date), then fallback to athlete profile
        weight_kg = None
        try:
            # Get latest wellness entry with weight
            wellness_data = client.get_wellness(days_back=90)
            if wellness_data and isinstance(wellness_data, list):
                # Iterate in REVERSE to get the MOST RECENT weight (last entry is most recent)
                for i in range(len(wellness_data) - 1, -1, -1):
                    entry = wellness_data[i]
                    # Try different field names for weight
                    weight_value = entry.get('weight') or entry.get('weight_kg') or entry.get('weightKg')
                    if weight_value:
                        weight_kg = weight_value
                        break  # Take the most recent one with weight
        except Exception as e:
            pass  # Fall back to athlete profile if wellness fails
        
        # If no weight from wellness, try athlete profile
        if not weight_kg:
            weight_kg = athlete_data.get('weight') or athlete_data.get('weight_kg')

        # Extract metrics with fallbacks
        metrics = {
            'weight_kg': weight_kg,
            'height_cm': height_cm,
            'cp': cycling_settings.get('ftp') or cycling_settings.get('cp'),
            'w_prime': cycling_settings.get('w_prime') or cycling_settings.get('wPrime'),
            'ecp': mmp_model.get('criticalPower') or mmp_model.get('cp'),
            'ew_prime': mmp_model.get('wPrime') or mmp_model.get('w_prime'),
            'max_hr': athlete_data.get('maxHeartRate') or athlete_data.get('maxHR') or athlete_data.get('max_hr'),
        }
        
        # Update athlete in storage (only non-None values)
        update_data = {k: v for k, v in metrics.items() if v is not None}
        if update_data:
            storage.update_athlete(athlete_id, **update_data)
        
        updated_athlete = storage.get_athlete(athlete_id)
        
        return {
            "success": True,
            "message": "Athlete metrics synced successfully",
            "athlete": updated_athlete,
            "synced_fields": update_data
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
