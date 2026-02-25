"""Intervals.icu Sync API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import logging
from datetime import datetime, timedelta

from shared.intervals.sync import IntervalsSyncService
from shared.intervals.client import IntervalsAPIClient
from shared.storage import get_storage

router = APIRouter()

logger = logging.getLogger(__name__)


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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Connection failed: {str(e)}")


@router.post("/activities")
async def sync_activities(request: SyncRequest):
    """Sync activities from Intervals.icu"""
    try:
        storage = get_storage()
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
                logger.warning(f"Error importing activity: {e}")
                continue

        return {
            "success": True,
            "message": f"Imported {imported_count} activities, skipped {skipped_count} duplicates",
            "imported": imported_count,
            "skipped": skipped_count,
            "total": len(activities)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/wellness")
async def sync_wellness(request: WellnessSyncRequest):
    """Sync wellness data from Intervals.icu"""
    try:
        storage = get_storage()
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
                logger.warning(f"Error importing wellness entry: {e}")
                continue

        return {
            "success": True,
            "message": f"Imported {imported_count} wellness entries",
            "imported": imported_count,
            "total_found": len(wellness_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/athlete-metrics")
async def sync_athlete_metrics(request: SyncRequest):
    """Sync athlete metrics (weight, FTP, W', height, eCP, eW', HR max, gender, birth_date) from Intervals.icu"""
    try:
        storage = get_storage()
        api_key = request.api_key

        if not api_key or not api_key.strip():
            raise HTTPException(status_code=400, detail="API key non fornita per l'atleta")

        logger.info(f"[SYNC] Starting athlete metrics sync for athlete_id={request.athlete_id}")

        client = IntervalsAPIClient(api_key=api_key)

        try:
            athlete_data = client.get_athlete()
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Failed to connect to Intervals.icu: {str(e)}")

        updates: dict = {}

        # ===== Weight =====
        weight = athlete_data.get('weight')
        if weight:
            try:
                updates['weight_kg'] = float(weight)
            except (ValueError, TypeError):
                pass

        # ===== Height (convert from meters to cm) =====
        height = athlete_data.get('height')
        if height:
            try:
                height_m = float(height)
                if height_m > 0:
                    updates['height_cm'] = height_m * 100
            except (ValueError, TypeError):
                pass

        # ===== Power data from sportSettings (cycling sport settings) =====
        sport_settings = athlete_data.get('sportSettings', [])
        if sport_settings and len(sport_settings) > 0:
            cycling_settings = sport_settings[0]  # First sport is cycling
            
            # FTP = Critical Power
            ftp = cycling_settings.get('ftp')
            if ftp:
                try:
                    updates['cp'] = float(ftp)
                except (ValueError, TypeError):
                    pass
            
            # W Prime (W')
            w_prime = cycling_settings.get('w_prime')
            if w_prime:
                try:
                    updates['w_prime'] = float(w_prime)
                except (ValueError, TypeError):
                    pass
            
            # Max heart rate
            max_hr = cycling_settings.get('max_heartrate')
            if max_hr:
                try:
                    updates['max_hr'] = float(max_hr)
                except (ValueError, TypeError):
                    pass
            
            # Estimated values from MMP Model (more accurate, calculated by Intervals)
            mmp_model = cycling_settings.get('mmp_model', {})
            if mmp_model:
                # Estimated Critical Power
                ecp = mmp_model.get('criticalPower')
                if ecp:
                    try:
                        updates['ecp'] = float(ecp)
                    except (ValueError, TypeError):
                        pass
                
                # Estimated W Prime
                ew_prime = mmp_model.get('wPrime')
                if ew_prime:
                    try:
                        updates['ew_prime'] = float(ew_prime)
                    except (ValueError, TypeError):
                        pass

        # ===== Gender =====
        gender_raw = (
            athlete_data.get('gender') or
            athlete_data.get('sex') or
            athlete_data.get('athleteGender') or ''
        )
        if gender_raw:
            # Map to Italian gender names (Maschile/Femminile) as stored in database
            gender_map = {
                'male': 'Maschile',
                'female': 'Femminile',
                'm': 'Maschile',
                'f': 'Femminile',
                '0': 'Maschile',
                '1': 'Femminile',
                'maschile': 'Maschile',
                'femminile': 'Femminile'
            }
            updates['gender'] = gender_map.get(str(gender_raw).lower(), str(gender_raw))

        # ===== Birth date =====
        birth_date_raw = (
            athlete_data.get('birthDate') or
            athlete_data.get('dateOfBirth') or
            athlete_data.get('birth_date') or ''
        )
        if birth_date_raw:
            updates['birth_date'] = str(birth_date_raw)[:10]

        if not updates:
            return {"success": True, "message": "Nessun dato disponibile da sincronizzare", "synced_fields": {}}

        storage.update_athlete(request.athlete_id, **updates)

        return {
            "success": True,
            "message": f"Sincronizzate {len(updates)} metriche",
            "synced_fields": updates,
            "updated_fields": list(updates.keys())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/push-race")
async def push_race(request: PushRaceRequest):
    """Push a race to Intervals.icu as a planned event for all enrolled athletes using their own API keys"""
    try:
        storage = get_storage()
        logger.info(f"[PUSH-RACE] race_id={request.race_id}")

        race = storage.get_race(request.race_id)
        if not race:
            raise HTTPException(status_code=404, detail=f"Race not found (ID: {request.race_id})")

        # Get all athletes for this race
        race_athletes = race.get('athletes', [])
        if not race_athletes:
            raise HTTPException(status_code=400, detail="No athletes enrolled in this race")

        # Filter athletes with API keys
        athletes_with_keys = []
        for athlete_data in race_athletes:
            athlete_id = athlete_data.get('id')
            athlete = storage.get_athlete(athlete_id)
            if athlete and athlete.get('api_key'):
                athletes_with_keys.append({
                    'data': athlete_data,
                    'profile': athlete,
                    'api_key': athlete.get('api_key')
                })
        
        if not athletes_with_keys:
            raise HTTPException(status_code=400, detail="No athletes in this race have an API key configured")

        # Prepare race data (common for all athletes)
        distance_km = race.get('distance_km') or 0
        elevation_m = race.get('elevation_m') or 0
        predicted_kj = race.get('predicted_kj') or 0
        category = race.get('category') or 'C'
        notes = race.get('notes') or ''

        predicted_duration = race.get('predicted_duration_minutes')
        duration_minutes = float(predicted_duration) if predicted_duration else (
            (distance_km / 38.5) * 60 if distance_km > 0 else 240
        )
        duration_seconds = int(duration_minutes * 60)

        start_date_local = f"{race['race_date']}T10:00:00"
        start_dt = datetime.fromisoformat(start_date_local)
        end_dt = start_dt + timedelta(seconds=duration_seconds)
        end_date_local = end_dt.isoformat()

        category_upper = str(category).upper()
        intervals_category = f"RACE_{category_upper}" if category_upper in ['A', 'B', 'C'] else "RACE_C"

        def format_duration(minutes: float) -> str:
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours}h {mins}m"

        race_name = race['name']

        # Push race to each athlete with API key
        pushed_count = 0
        failed_athletes = []
        
        for athlete_info in athletes_with_keys:
            try:
                athlete_id = athlete_info['data'].get('id')
                athlete = athlete_info['profile']
                api_key = athlete_info['api_key']
                
                client = IntervalsAPIClient(api_key=api_key)

                # Build description with athlete-specific data
                race_description = (
                    f'<div><b>{race_name}</b></div>'
                    f'<div><b><span class="text-blue">Distanza</span>: {distance_km:.1f} km</b></div>'
                    f'<div><b><span class="text-red-darken-2">Dislivello</span>: {int(elevation_m)}m</b></div>'
                    f'<div><b><span class="text-green">Previsti</span>: {int(predicted_kj)}kJ'
                )

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

                # Add athlete-specific info
                objective = athlete_info['data'].get('objective', 'C')
                kj_per_h_kg = athlete_info['data'].get('kj_per_hour_per_kg', 10.0)
                race_description += f'<div><b>Atleta</b>: {athlete.get("first_name")} {athlete.get("last_name")} | ' \
                                   f'<b>Obiettivo</b>: {objective} | ' \
                                   f'<b>kJ/h/kg</b>: {kj_per_h_kg:.1f}</div>'

                # Check for duplicate in this specific athlete's calendar
                try:
                    existing_events = client.get_events(
                        athlete_id="0",
                        oldest=start_date_local[:10],
                        newest=start_date_local[:10],
                        days_forward=1
                    )
                    
                    event_exists = any(
                        evt.get('name') == race_name 
                        for evt in existing_events
                    )
                    
                    if event_exists:
                        logger.info(f"[PUSH-RACE] Race '{race_name}' already exists for athlete {athlete_id}")
                        continue
                except Exception as check_err:
                    logger.warning(f"Could not check duplicate for athlete {athlete_id}: {check_err}")

                event = client.create_event(
                    athlete_id="0",
                    category=intervals_category,
                    start_date_local=start_date_local,
                    end_date_local=end_date_local,
                    name=race_name,
                    description=race_description,
                    activity_type='Ride',
                    distance=distance_km * 1000,  # km → meters
                    moving_time=duration_seconds
                )

                pushed_count += 1
                logger.info(f"[PUSH-RACE] Pushed to athlete {athlete_id}: {athlete.get('first_name')} {athlete.get('last_name')}")

            except Exception as e:
                athlete_id = athlete_info['data'].get('id')
                failed_athletes.append(f"Athlete {athlete_id}: {str(e)}")
                logger.error(f"[PUSH-RACE] Failed to push to athlete {athlete_id}: {e}")

        return {
            "success": True,
            "message": f"Race pushed to {pushed_count} athletes",
            "athletes_processed": pushed_count,
            "total_athletes": len(athletes_with_keys),
            "failed_athletes": failed_athletes if failed_athletes else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/debug/races")
async def debug_list_races():
    """Debug endpoint to list all races in database"""
    try:
        from shared.storage import Race
        storage = get_storage()
        races = storage.session.query(Race.id, Race.name, Race.race_date).all()
        return {
            "total": len(races),
            "races": [{"id": r.id, "name": r.name, "date": r.race_date} for r in races]
        }
    except Exception as e:
        return {"error": str(e)}


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
