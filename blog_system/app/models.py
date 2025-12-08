from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship
from app.database import Base

# Ассоциативная таблица для связи многие-ко-многим постов и категорий
post_categories = Table(
    "post_categories",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    """Модель пользователя."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    bio = Column(Text)
    profile_picture = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Связи
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    
    # Подписки: пользователи, на которых подписан этот пользователь
    subscriptions = relationship(
        "Subscription",
        foreign_keys="Subscription.subscriber_id",
        back_populates="subscriber",
        cascade="all, delete-orphan",
    )
    
    # Подписчики: пользователи, которые подписаны на этого пользователя
    subscribers = relationship(
        "Subscription",
        foreign_keys="Subscription.subscribed_to_id",
        back_populates="subscribed_to",
        cascade="all, delete-orphan",
    )


class Category(Base):
    """Модель категории (тэга)."""
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    posts = relationship("Post", secondary=post_categories, back_populates="categories")


class Post(Base):
    """Модель поста блога."""
    
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text)
    status = Column(String(20), default="draft")  # draft, published, archived
    featured_image = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    view_count = Column(Integer, default=0)
    
    # Ограничение уникальности
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'published', 'archived')", name="check_post_status"),
    )
    
    # Связи
    author = relationship("User", back_populates="posts")
    categories = relationship("Category", secondary=post_categories, back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    """Модель комментария."""
    
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Связи
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")


class Favorite(Base):
    """Модель избранного поста."""
    
    __tablename__ = "favorites"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("User", back_populates="favorites")
    post = relationship("Post", back_populates="favorites")


class Subscription(Base):
    """Модель подписки пользователя на другого пользователя."""
    
    __tablename__ = "subscriptions"
    
    subscriber_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    subscribed_to_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Ограничение: нельзя подписаться на себя
    __table_args__ = (
        CheckConstraint("subscriber_id != subscribed_to_id", name="check_no_self_subscription"),
    )
    
    # Связи
    subscriber = relationship(
        "User",
        foreign_keys=[subscriber_id],
        back_populates="subscriptions",
    )
    subscribed_to = relationship(
        "User",
        foreign_keys=[subscribed_to_id],
        back_populates="subscribers",
    )