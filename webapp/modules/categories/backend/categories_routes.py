"""Categories API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path

from shared.storage import BTeamStorage

router = APIRouter()

# Get storage instance
storage_dir = Path(__file__).resolve().parent.parent.parent.parent / "data"
storage = BTeamStorage(storage_dir)


class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str
    created_at: str


@router.get("/", response_model=List[CategoryResponse])
async def get_categories():
    """Get all categories"""
    categories = storage.list_categories()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int):
    """Get a specific category by ID"""
    category = storage.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate):
    """Create a new category"""
    try:
        category_id = storage.add_category(name=category.name)
        created_category = storage.get_category(category_id)
        if not created_category:
            raise HTTPException(status_code=500, detail="Failed to retrieve created category")
        return created_category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, category: CategoryCreate):
    """Update an existing category"""
    categories = storage.list_categories()
    existing_category = next((c for c in categories if c['id'] == category_id), None)
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")

    try:
        storage.update_category(category_id, name=category.name)
        updated_category = {
            "id": category_id,
            "name": category.name,
            "created_at": existing_category["created_at"]
        }
        return updated_category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}")
async def delete_category(category_id: int):
    """Delete a category"""
    categories = storage.list_categories()
    existing_category = next((c for c in categories if c['id'] == category_id), None)
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")

    try:
        storage.delete_category(category_id)
        return {"message": "Category deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
