from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas, models
from app.database import get_db

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/", response_model=List[schemas.CategoryInDB])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить список всех категорий.
    """
    result = await db.execute(
        select(models.Category).offset(skip).limit(limit)
    )
    categories = result.scalars().all()
    return categories


@router.get("/{category_id}", response_model=schemas.CategoryInDB)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить категорию по ID.
    """
    result = await db.execute(
        select(models.Category).where(models.Category.id == category_id)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    return category


@router.post("/", response_model=schemas.CategoryInDB)
async def create_category(
    category: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Создать новую категорию.
    """
    # Генерируем slug из имени
    slug = category.name.lower().replace(" ", "-")
    
    db_category = models.Category(
        name=category.name,
        slug=slug,
        description=category.description,
    )
    
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    
    return db_category


@router.put("/{category_id}", response_model=schemas.CategoryInDB)
async def update_category(
    category_id: int,
    category_update: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Обновить категорию.
    """
    result = await db.execute(
        select(models.Category).where(models.Category.id == category_id)
    )
    db_category = result.scalar_one_or_none()
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    # Обновляем поля
    db_category.name = category_update.name
    db_category.slug = category_update.name.lower().replace(" ", "-")
    db_category.description = category_update.description
    
    await db.commit()
    await db.refresh(db_category)
    
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Удалить категорию.
    """
    result = await db.execute(
        select(models.Category).where(models.Category.id == category_id)
    )
    db_category = result.scalar_one_or_none()
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    await db.delete(db_category)
    await db.commit()
    
    return None