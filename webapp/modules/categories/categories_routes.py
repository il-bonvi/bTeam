"""Categories API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from shared.storage import get_storage

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str
    created_at: str


@router.get("/", response_model=List[CategoryResponse])
async def get_categories():
    """Get all categories"""
    return get_storage().list_categories()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int):
    """Get a specific category by ID"""
    category = get_storage().get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate):
    """Create a new category"""
    try:
        storage = get_storage()
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
    storage = get_storage()
    if not storage.get_category(category_id):
        raise HTTPException(status_code=404, detail="Category not found")

    try:
        storage.update_category(category_id, name=category.name)
        return storage.get_category(category_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}")
async def delete_category(category_id: int):
    """Delete a category"""
    storage = get_storage()
    if not storage.get_category(category_id):
        raise HTTPException(status_code=404, detail="Category not found")

    try:
        storage.delete_category(category_id)
        return {"message": "Category deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
