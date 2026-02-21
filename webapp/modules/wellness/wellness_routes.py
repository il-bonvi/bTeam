"""Wellness API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from shared.storage import get_storage

router = APIRouter()


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
    injury: Optional[float] = None
    kcal: Optional[int] = None
    sleep_secs: Optional[int] = None
    sleep_score: Optional[int] = None
    sleep_quality: Optional[int] = None
    avg_sleeping_hr: Optional[float] = None
    menstruation: Optional[bool] = None
    menstrual_cycle_phase: Optional[int] = None
    body_fat: Optional[float] = None
    respiration: Optional[float] = None
    spO2: Optional[float] = None
    readiness: Optional[float] = None
    ctl: Optional[float] = None
    atl: Optional[float] = None
    ramp_rate: Optional[float] = None
    comments: Optional[str] = None


def _find_wellness_by_id(wellness_id: int):
    """
    Helper: cerca un entry wellness per ID.
    Scansiona tutti gli atleti cercando l'entry con l'ID dato.
    """
    storage = get_storage()
    for athlete in storage.list_athletes():
        athlete_id = int(athlete['id'])
        for entry in storage.get_wellness(athlete_id, days_back=365):
            if entry.get('id') == wellness_id:
                return entry
    return None


@router.get("/")
async def get_wellness(athlete_id: Optional[int] = None, days_back: int = 30):
    """Get wellness data, optionally filtered by athlete"""
    storage = get_storage()
    if athlete_id:
        return storage.get_wellness(athlete_id, days_back=days_back)

    wellness_data = []
    for athlete in storage.list_athletes():
        wellness_data.extend(storage.get_wellness(int(athlete['id']), days_back=days_back))
    return wellness_data


@router.get("/athlete/{athlete_id}/latest")
async def get_latest_wellness(athlete_id: int):
    """Get the latest wellness entry for an athlete"""
    wellness_data = get_storage().get_wellness(athlete_id, days_back=7)
    if not wellness_data:
        raise HTTPException(status_code=404, detail="No wellness data found")
    return wellness_data[0]


@router.get("/{wellness_id}")
async def get_wellness_entry(wellness_id: int):
    """Get a specific wellness entry by ID"""
    entry = _find_wellness_by_id(wellness_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Wellness entry not found")
    return entry


@router.post("/")
async def create_wellness_entry(wellness: WellnessCreate):
    """Create or update a wellness entry"""
    try:
        storage = get_storage()
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
            injury=wellness.injury,
            kcal=wellness.kcal,
            sleep_secs=wellness.sleep_secs,
            sleep_score=wellness.sleep_score,
            sleep_quality=wellness.sleep_quality,
            avg_sleeping_hr=wellness.avg_sleeping_hr,
            menstruation=wellness.menstruation,
            menstrual_cycle_phase=wellness.menstrual_cycle_phase,
            body_fat=wellness.body_fat,
            respiration=wellness.respiration,
            spO2=wellness.spO2,
            readiness=wellness.readiness,
            ctl=wellness.ctl,
            atl=wellness.atl,
            ramp_rate=wellness.ramp_rate,
            comments=wellness.comments
        )
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create wellness entry")

        # Restituisce il record appena creato/aggiornato
        wellness_data = storage.get_wellness(wellness.athlete_id, days_back=7)
        for entry in wellness_data:
            if entry.get('wellness_date') == wellness.wellness_date:
                return entry
        return {"message": "Wellness entry created/updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{wellness_id}")
async def update_wellness_entry(wellness_id: int, wellness: WellnessCreate):
    """Update a wellness entry"""
    if not _find_wellness_by_id(wellness_id):
        raise HTTPException(status_code=404, detail="Wellness entry not found")

    try:
        storage = get_storage()
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
            injury=wellness.injury,
            kcal=wellness.kcal,
            sleep_secs=wellness.sleep_secs,
            sleep_score=wellness.sleep_score,
            sleep_quality=wellness.sleep_quality,
            avg_sleeping_hr=wellness.avg_sleeping_hr,
            menstruation=wellness.menstruation,
            menstrual_cycle_phase=wellness.menstrual_cycle_phase,
            body_fat=wellness.body_fat,
            respiration=wellness.respiration,
            spO2=wellness.spO2,
            readiness=wellness.readiness,
            ctl=wellness.ctl,
            atl=wellness.atl,
            ramp_rate=wellness.ramp_rate,
            comments=wellness.comments
        )
        if result:
            return {"message": "Wellness entry updated successfully"}
        raise HTTPException(status_code=400, detail="Failed to update wellness entry")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{wellness_id}")
async def delete_wellness_entry(wellness_id: int):
    """Delete a wellness entry (not yet implemented in storage)"""
    raise HTTPException(status_code=501, detail="Delete wellness not implemented yet")
