"""
User Management Endpoints

Handles user CRUD operations and user management for administrators.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.user import User
from app.schemas.user import UserResponse, UserListResponse, UserUpdate, UserCreate

router = APIRouter()


async def get_current_superuser(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> str:
    """Dependency to check if current user is a superuser."""
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user_id


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    is_active: bool = Query(None),
    is_superuser: bool = Query(None),
    current_user_id: str = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List all users (admin only).
    
    Supports pagination, search, and filtering.
    """
    # Build query
    query = select(User)
    
    # Apply filters
    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            User.username.ilike(f"%{search}%"),
            User.full_name.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    if is_superuser is not None:
        query = query.where(User.is_superuser == is_superuser)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(User.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user_id: str = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get user by ID (admin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    current_user_id: str = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new user (admin only).
    """
    from app.core.security import PasswordManager
    
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if data.username:
        result = await db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create user
    user = User(
        email=data.email,
        username=data.username,
        full_name=data.full_name,
        password_hash=PasswordManager.hash_password(data.password),
        is_active=data.is_active if data.is_active is not None else True,
        is_verified=data.is_verified if data.is_verified is not None else False,
        is_superuser=data.is_superuser if data.is_superuser is not None else False,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    data: UserUpdate,
    current_user_id: str = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update user (admin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    
    # Handle password update
    if "password" in update_data and update_data["password"]:
        from app.core.security import get_password_hash
        user.password_hash = get_password_hash(update_data.pop("password"))
    
    # Check email uniqueness if being updated
    if "email" in update_data and update_data["email"] != user.email:
        result = await db.execute(select(User).where(User.email == update_data["email"]))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check username uniqueness if being updated
    if "username" in update_data and update_data["username"] != user.username:
        result = await db.execute(select(User).where(User.username == update_data["username"]))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user_id: str = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete user (admin only).
    
    Cannot delete yourself.
    """
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.delete(user)
    await db.commit()


@router.get("/stats/overview")
async def get_user_stats(
    current_user_id: str = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get user statistics (admin only).
    """
    # Total users
    total_result = await db.execute(select(func.count()).select_from(User))
    total_users = total_result.scalar()
    
    # Active users
    active_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_active == True)
    )
    active_users = active_result.scalar()
    
    # Verified users
    verified_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_verified == True)
    )
    verified_users = verified_result.scalar()
    
    # Superusers
    superuser_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_superuser == True)
    )
    superusers = superuser_result.scalar()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "verified_users": verified_users,
        "unverified_users": total_users - verified_users,
        "superusers": superusers,
        "regular_users": total_users - superusers,
    }
