"""Teams API Routes"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from storage_bteam import BTeamStorage

router = APIRouter()

# Get storage instance
storage_dir = Path(__file__).parent.parent.parent / "data"
storage = BTeamStorage(storage_dir)


class TeamCreate(BaseModel):
    name: str


class TeamResponse(BaseModel):
    id: int
    name: str
    created_at: str


@router.get("/", response_model=List[TeamResponse])
async def get_teams():
    """Get all teams"""
    teams = storage.get_all_teams()
    return teams


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int):
    """Get a specific team by ID"""
    team = storage.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("/", response_model=TeamResponse)
async def create_team(team: TeamCreate):
    """Create a new team"""
    try:
        new_team = storage.add_team(name=team.name)
        return new_team
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(team_id: int, team: TeamCreate):
    """Update an existing team"""
    existing_team = storage.get_team(team_id)
    if not existing_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    try:
        updated_team = storage.update_team(team_id, name=team.name)
        return updated_team
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{team_id}")
async def delete_team(team_id: int):
    """Delete a team"""
    existing_team = storage.get_team(team_id)
    if not existing_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    try:
        storage.delete_team(team_id)
        return {"message": "Team deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
