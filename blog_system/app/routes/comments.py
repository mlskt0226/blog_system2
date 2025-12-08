from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas, models
from app.database import get_db

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
)


@router.get("/post/{post_id}", response_model=List[schemas.CommentWithAuthor])
async def get_comments_by_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить комментарии для поста.
    """
    # Проверяем существование поста
    result = await db.execute(
        select(models.Post).where(models.Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    # Получаем корневые комментарии (без родителя)
    result = await db.execute(
        select(models.Comment)
        .where(models.Comment.post_id == post_id, models.Comment.parent_id.is_(None))
        .order_by(models.Comment.created_at)
    )
    comments = result.scalars().all()
    
    return comments


@router.post("/", response_model=schemas.CommentInDB)
async def create_comment(
    comment: schemas.CommentCreate,
    post_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Создать комментарий к посту.
    """
    # Проверяем существование поста
    result = await db.execute(
        select(models.Post).where(models.Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    # Если указан родительский комментарий, проверяем его существование
    if comment.parent_id:
        result = await db.execute(
            select(models.Comment).where(
                models.Comment.id == comment.parent_id,
                models.Comment.post_id == post_id,
            )
        )
        parent_comment = result.scalar_one_or_none()
        
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found",
            )
    
    db_comment = models.Comment(
        post_id=post_id,
        user_id=current_user.id,
        parent_id=comment.parent_id,
        content=comment.content,
    )
    
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    
    return db_comment


@router.put("/{comment_id}", response_model=schemas.CommentInDB)
async def update_comment(
    comment_id: int,
    comment_update: schemas.CommentBase,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Обновить комментарий.
    """
    result = await db.execute(
        select(models.Comment).where(models.Comment.id == comment_id)
    )
    db_comment = result.scalar_one_or_none()
    
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    # Проверяем, что пользователь является автором комментария
    if db_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    db_comment.content = comment_update.content
    
    await db.commit()
    await db.refresh(db_comment)
    
    return db_comment


@router.delete("/{comment