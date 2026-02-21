"""Teams API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from shared.storage import get_storage

router = APIRouter()


class TeamCreate(BaseModel):
    name: str


class TeamResponse(BaseModel):
    id: int
    name: str
    created_at: str


@router.get("/", response_model=List[TeamResponse])
async def get_teams():
    """Get all teams"""
    return get_storage().list_teams()


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int):
    """Get a specific team by ID"""
    team = get_storage().get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("/", response_model=TeamResponse)
async def create_team(team: TeamCreate):
    """Create a new team"""
    try:
        storage = get_storage()
        team_id = storage.add_team(name=team.name)
        # Recupera dal DB così created_at è quello reale
        new_team = storage.get_team(team_id)
        if not new_team:
            raise HTTPException(status_code=500, detail="Failed to retrieve created team")
        return new_team
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(team_id: int, team: TeamCreate):
    """Update an existing team"""
    storage = get_storage()
    existing_team = storage.get_team(team_id)
    if not existing_team:
        raise HTTPException(status_code=404, detail="Team not found")

    try:
        storage.update_team(team_id, name=team.name)
        return storage.get_team(team_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{team_id}")
async def delete_team(team_id: int):
    """Delete a team"""
    storage = get_storage()
    if not storage.get_team(team_id):
        raise HTTPException(status_code=404, detail="Team not found")

    try:
        storage.delete_team(team_id)
        return {"message": "Team deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
