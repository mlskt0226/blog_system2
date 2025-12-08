from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator, ConfigDict


# Базовые схемы
class BaseSchema(BaseModel):
    """Базовая схема с общей конфигурацией."""
    
    model_config = ConfigDict(from_attributes=True)


# Схемы для пользователей
class UserBase(BaseSchema):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserUpdate(BaseSchema):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None


class UserInDB(UserBase):
    id: int
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool


class UserPublic(UserInDB):
    pass


# Схемы для категорий
class CategoryBase(BaseSchema):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryInDB(CategoryBase):
    id: int
    slug: str
    created_at: datetime


# Схемы для постов
class PostBase(BaseSchema):
    title: str
    content: str
    excerpt: Optional[str] = None
    status: str = "draft"
    featured_image: Optional[str] = None


class PostCreate(PostBase):
    category_ids: List[int] = []


class PostUpdate(BaseSchema):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    status: Optional[str] = None
    featured_image: Optional[str] = None
    category_ids: Optional[List[int]] = None


class PostInDB(PostBase):
    id: int
    user_id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    view_count: int = 0


class PostWithAuthor(PostInDB):
    author: UserPublic
    categories: List[CategoryInDB] = []


# Схемы для комментариев
class CommentBase(BaseSchema):
    content: str


class CommentCreate(CommentBase):
    parent_id: Optional[int] = None


class CommentInDB(CommentBase):
    id: int
    post_id: int
    user_id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False


class CommentWithAuthor(CommentInDB):
    author: UserPublic
    replies: List["CommentWithAuthor"] = []


# Схемы для избранного
class FavoriteBase(BaseSchema):
    pass


class FavoriteCreate(FavoriteBase):
    post_id: int


class FavoriteInDB(FavoriteBase):
    user_id: int
    post_id: int
    created_at: datetime


# Схемы для подписок
class SubscriptionBase(BaseSchema):
    pass


class SubscriptionCreate(SubscriptionBase):
    subscribed_to_id: int


class SubscriptionInDB(SubscriptionBase):
    subscriber_id: int
    subscribed_to_id: int
    created_at: datetime


class SubscriptionWithUser(SubscriptionInDB):
    subscribed_to: UserPublic


# Обновляем рекурсивные типы
CommentWithAuthor.model_rebuild()