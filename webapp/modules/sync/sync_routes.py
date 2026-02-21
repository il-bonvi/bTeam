"""Intervals.icu Sync API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import logging

from shared.intervals.sync import IntervalsSyncService
from shared.intervals.client import IntervalsAPIClient
from shared.storage import BTeamStorage

router = APIRouter()

logger = logging.getLogger(__name__)

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

        imported_count = 0
        for entry in wellness_data:
            try:
                wellness_date = entry.get('id')
                if not wellness_date:
                    continue
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
                    menstruation=None,
                    menstrual_cycle_phase=entry.get('menstrualPhase'),
                    body_fat=entry.get('bodyFat'),
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


@router.get("/debug/races")
async def debug_list_races():
    """Debug endpoint to list all races in database"""
    try:
        from shared.storage import Race
        races = storage.session.query(Race.id, Race.name, Race.race_date).all()
        return {
            "total": len(races),
            "races": [{"id": r.id, "name": r.name, "date": r.race_date} for r in races]
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/push-race")
async def push_race(request: PushRaceRequest):
    """Push a race to Intervals.icu as a planned event"""
    try:
        logger.info(f"[PUSH-RACE] race_id={request.race_id}, athlete_id={request.athlete_id}")

        race = storage.get_race(request.race_id)
        if not race:
            raise HTTPException(status_code=404, detail=f"Race not found (ID: {request.race_id})")

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

        # Calculate duration
        predicted_duration = race.get('predicted_duration_minutes')
        if predicted_duration:
            duration_minutes = float(predicted_duration)
        else:
            duration_minutes = (distance_km / 38.5) * 60 if distance_km > 0 else 240

        duration_seconds = int(duration_minutes * 60)

        # Build start/end dates
        from datetime import datetime, timedelta
        start_date_local = f"{race['race_date']}T10:00:00"
        start_dt = datetime.fromisoformat(start_date_local)
        end_dt = start_dt + timedelta(seconds=duration_seconds)
        end_date_local = end_dt.isoformat()

        # Map category A/B/C → RACE_A/RACE_B/RACE_C
        category_upper = str(category).upper()
        intervals_category = f"RACE_{category_upper}" if category_upper in ['A', 'B', 'C'] else "RACE_C"

        def format_duration(minutes):
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours}h {mins}m"

        # Build HTML description (same as OLDAPP)
        race_description = f'<div><b><span class="text-red-darken-2">Dislivello</span>: {int(elevation_m)}m</b></div>'
        race_description += f'<div><b><span class="text-green">Previsti</span>: {int(predicted_kj)}kJ'

        athlete_weight = athlete.get('weight_kg')
        if athlete_weight and predicted_kj > 0 and duration_minutes > 0:
            kj_per_hour = predicted_kj / (duration_minutes / 60)
            kj_per_h_kg = kj_per_hour / float(athlete_weight)
            race_description += f' ({kj_per_h_kg:.1f} kJ/h/kg)'
        race_description += '</b></div>'

        if distance_km > 0:
            duration_36_str = format_duration((distance_km / 36.0) * 60)
            duration_41_str = format_duration((distance_km / 41.0) * 60)
            race_description += (
                f'<div><b><span class="text-blue">avg 36 km/h</span>: {duration_36_str}</b>'
                f'<br><b><span class="text-blue-darken-4">avg 41 km/h</span>: {duration_41_str}</b></div>'
            )

        if notes:
            race_description += f'<div><b><span class="text-purple">Note</span>: {notes}</b></div>'

        result = client.create_event(
            athlete_id="0",
            category=intervals_category,
            start_date_local=start_date_local,
            end_date_local=end_date_local,
            name=race['name'],
            description=race_description,
            activity_type='Ride',
            distance=distance_km * 1000,  # km → meters
            moving_time=duration_seconds
        )

        return {
            "success": True,
            "message": "Race pushed to Intervals.icu successfully",
            "event_id": result.get('id')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/debug/athlete-data/{api_key}")
async def debug_athlete_data(api_key: str):
    """Debug endpoint to see raw athlete data from Intervals.icu"""
    try:
        client = IntervalsAPIClient(api_key=api_key)
        athlete_data = client.get_athlete()
        return {
            "gender_field_value": athlete_data.get('gender'),
            "sex_field_value": athlete_data.get('sex'),
            "all_keys": list(athlete_data.keys()),
            "full_athlete_data": athlete_data
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/athlete-metrics")
async def sync_athlete_metrics(request: SyncRequest):
    """Sync athlete metrics from Intervals.icu"""
    try:
        athlete_id = request.athlete_id
        api_key = request.api_key

        if not api_key or not api_key.strip():
            raise HTTPException(status_code=400, detail="API key non fornita per l'atleta")

        logger.info(f"[SYNC] Starting athlete metrics sync for athlete_id={athlete_id}")

        client = IntervalsAPIClient(api_key=api_key)

        try:
            athlete_data = client.get_athlete()
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Failed to connect to Intervals.icu: {str(e)}")

        updates = {}

        weight = athlete_data.get('weight')
        if weight:
            updates['weight_kg'] = float(weight)

        ftp = athlete_data.get('icu_ftp')
        if ftp:
            updates['cp'] = float(ftp)

        max_hr = athlete_data.get('icu_hr_max')
        if max_hr:
            updates['max_hr'] = float(max_hr)

        gender_raw = (
            athlete_data.get('gender') or
            athlete_data.get('sex') or
            athlete_data.get('athleteGender') or ''
        )
        if gender_raw:
            gender_map = {'male': 'M', 'female': 'F', 'm': 'M', 'f': 'F', '0': 'M', '1': 'F'}
            updates['gender'] = gender_map.get(str(gender_raw).lower(), str(gender_raw))

        birth_date_raw = (
            athlete_data.get('birthDate') or
            athlete_data.get('dateOfBirth') or
            athlete_data.get('birth_date') or ''
        )
        if birth_date_raw:
            updates['birth_date'] = str(birth_date_raw)[:10]

        if not updates:
            return {"success": True, "message": "No metrics to update", "updated_fields": []}

        storage.update_athlete(athlete_id, **updates)

        return {
            "success": True,
            "message": f"Updated {len(updates)} metrics",
            "updated_fields": list(updates.keys())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
