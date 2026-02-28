"""Races API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from shared.storage import get_storage

router = APIRouter()


class RaceCreate(BaseModel):
    name: str
    race_date_start: str
    race_date_end: str
    distance_km: Optional[float] = None
    num_stages: int = 1
    gender: Optional[str] = None
    category: Optional[str] = None
    elevation_m: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    predicted_duration_minutes: Optional[float] = None
    predicted_kj: Optional[float] = None
    route_file: Optional[str] = None
    notes: Optional[str] = None


class RaceAthleteAdd(BaseModel):
    athlete_id: int
    kj_per_hour_per_kg: float = 10.0
    objective: str = "C"


class StageUpdate(BaseModel):
    distance_km: Optional[float] = None
    elevation_m: Optional[float] = None
    route_file: Optional[str] = None
    notes: Optional[str] = None
    stage_date: Optional[str] = None
    avg_speed_kmh: Optional[float] = None


@router.get("/")
async def get_races():
    """Get all races"""
    return get_storage().list_races()


@router.get("/{race_id}")
async def get_race(race_id: int):
    """Get a specific race by ID"""
    race = get_storage().get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race


@router.post("/")
async def create_race(race: RaceCreate):
    """Create a new race"""
    try:
        storage = get_storage()
        race_id = storage.add_race(
            name=race.name,
            race_date_start=race.race_date_start,
            race_date_end=race.race_date_end,
            distance_km=race.distance_km,
            num_stages=race.num_stages,
            gender=race.gender,
            category=race.category,
            elevation_m=race.elevation_m,
            avg_speed_kmh=race.avg_speed_kmh,
            predicted_duration_minutes=race.predicted_duration_minutes,
            predicted_kj=race.predicted_kj,
            route_file=race.route_file,
            notes=race.notes
        )
        return storage.get_race(race_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{race_id}")
async def update_race(race_id: int, race: RaceCreate):
    """Update an existing race"""
    storage = get_storage()
    if not storage.get_race(race_id):
        raise HTTPException(status_code=404, detail="Race not found")

    try:
        storage.update_race(
            race_id=race_id,
            name=race.name,
            race_date_start=race.race_date_start,
            race_date_end=race.race_date_end,
            distance_km=race.distance_km,
            num_stages=race.num_stages,
            gender=race.gender,
            category=race.category,
            elevation_m=race.elevation_m,
            avg_speed_kmh=race.avg_speed_kmh,
            predicted_duration_minutes=race.predicted_duration_minutes,
            predicted_kj=race.predicted_kj,
            route_file=race.route_file,
            notes=race.notes
        )
        return storage.get_race(race_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{race_id}")
async def delete_race(race_id: int):
    """Delete a race"""
    storage = get_storage()
    if not storage.get_race(race_id):
        raise HTTPException(status_code=404, detail="Race not found")

    try:
        storage.delete_race(race_id)
        return {"message": "Race deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{race_id}/athletes")
async def add_athlete_to_race(race_id: int, athlete_data: RaceAthleteAdd):
    """Add an athlete to a race"""
    storage = get_storage()
    if not storage.get_race(race_id):
        raise HTTPException(status_code=404, detail="Race not found")
    if not storage.get_athlete(athlete_data.athlete_id):
        raise HTTPException(status_code=404, detail="Athlete not found")

    try:
        storage.add_athlete_to_race(
            race_id=race_id,
            athlete_id=athlete_data.athlete_id,
            kj_per_hour_per_kg=athlete_data.kj_per_hour_per_kg,
            objective=athlete_data.objective
        )
        return {"message": "Athlete added to race successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{race_id}/athletes/{athlete_id}")
async def update_athlete_in_race(race_id: int, athlete_id: int, athlete_data: RaceAthleteAdd):
    """Update athlete's objective and kJ value in a race"""
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        # Update the athlete's objective and kJ value using the proper storage method
        success = storage.update_race_athlete(
            race_id=race_id,
            athlete_id=athlete_id,
            objective=athlete_data.objective,
            kj_per_hour_per_kg=athlete_data.kj_per_hour_per_kg
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Athlete not found in this race")
        
        return {"message": "Athlete updated in race successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{race_id}/athletes/{athlete_id}")
async def remove_athlete_from_race(race_id: int, athlete_id: int):
    """Remove an athlete from a race"""
    try:
        get_storage().remove_athlete_from_race(race_id, athlete_id)
        return {"message": "Athlete removed from race successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{race_id}/athletes")
async def get_race_athletes(race_id: int):
    """Get all athletes for a race"""
    race = get_storage().get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race.get('athletes', [])


# ============ STAGE MANAGEMENT ENDPOINTS ============

@router.get("/{race_id}/stages")
async def get_race_stages(race_id: int):
    """Get all stages for a race"""
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        stages = storage.get_stages(race_id)
        return [stage.to_dict() if hasattr(stage, 'to_dict') else stage for stage in stages]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{race_id}/stages/{stage_id}")
async def get_stage(race_id: int, stage_id: int):
    """Get a specific stage by ID"""
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        stage = storage.get_stage(stage_id)
        if not stage:
            raise HTTPException(status_code=404, detail="Stage not found")
        return stage.to_dict() if hasattr(stage, 'to_dict') else stage
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{race_id}/stages")
async def create_stage(race_id: int, stage: StageUpdate):
    """Create a new stage for a race"""
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        # Get current number of stages to determine next stage number
        current_stages = storage.get_stages(race_id)
        stage_number = len(current_stages) + 1
        
        # Add the new stage
        stage_id = storage.add_stage(
            race_id=race_id,
            stage_number=stage_number,
            distance_km=stage.distance_km,
            elevation_m=stage.elevation_m,
            route_file=stage.route_file,
            notes=stage.notes
        )
        
        new_stage = storage.get_stage(stage_id)
        return new_stage.to_dict() if hasattr(new_stage, 'to_dict') else new_stage
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{race_id}/stages/{stage_id}")
async def update_stage(race_id: int, stage_id: int, stage: StageUpdate):
    """Update a specific stage"""
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        existing_stage = storage.get_stage(stage_id)
        if not existing_stage:
            raise HTTPException(status_code=404, detail="Stage not found")
        
        # Update the stage with provided data
        storage.update_stage(
            stage_id=stage_id,
            distance_km=stage.distance_km,
            elevation_m=stage.elevation_m,
            route_file=stage.route_file,
            notes=stage.notes,
            stage_date=stage.stage_date,
            avg_speed_kmh=stage.avg_speed_kmh
        )
        
        updated_stage = storage.get_stage(stage_id)
        return updated_stage.to_dict() if hasattr(updated_stage, 'to_dict') else updated_stage
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{race_id}/stages/{stage_id}")
async def delete_stage(race_id: int, stage_id: int):
    """Delete a specific stage"""
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        stage = storage.get_stage(stage_id)
        if not stage:
            raise HTTPException(status_code=404, detail="Stage not found")
        
        storage.delete_stage(stage_id)
        return {"message": "Stage deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

