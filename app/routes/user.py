from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, desc
from app.models import User
from app.schema import UserBase, UserRead, SuccessResponse, ErrorResponse
from app.responses import success_message, already_exists, internal_error, not_found
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

user = APIRouter()

@user.post(
    "/users", 
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        409: {"model": ErrorResponse, "description": "Username already exists"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Create a new user",
    description="Creates a user and returns the username if successful.",
    tags=["User"],
)
async def create_user(user: UserBase, db: AsyncSession = Depends(get_db)):
    new_username = User(
        username = (user.username).lower()
        )
    
    db.add(new_username)
    
    try:
        await db.commit()
        await db.refresh(new_username)
    except IntegrityError:
        await db.rollback()
        raise already_exists(new_username.username)
    except Exception:
        await db.rollback()
        raise internal_error()
    return success_message("created", new_username.username)


@user.get(
        "/users/{user_id}", 
        status_code=status.HTTP_200_OK,
        responses={
            404: {"model": ErrorResponse, "description": "User not found"},
            500: {"model": ErrorResponse, "description": "Internal Server Error"},
            },
        summary="Retrieve a user by ID",
        description="Fetches a user by their unique ID and returns their details if found.",
        tags=["User"],
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    
    if user is None:
        raise not_found("User")
    return user


@user.get(
    "/users",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserRead, "description": "List of users"},
        404: {"model": SuccessResponse, "description": "No users found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Get all users",
    description="Retrieves all users. Returns a message if no users are found.",
    tags=["User"],
)
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(User).order_by(desc(User.id)))
    users = result.all()
    
    if not users:
        return {'message': 'No users found'}
    return users


@user.patch(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "User not found"},
        409: {"model": ErrorResponse, "description": "Username already exists"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Update a user",
    description="Updates a user's username by ID and returns a status message.",
    tags=["User"],
)
async def update_user(user_id: int, user: UserBase, db: AsyncSession = Depends(get_db)):
    
    db_user = await db.get(User, user_id)
    
    if db_user is None:
        raise not_found("User")
    
    db_user.username = user.username  # Only update allowed fields

    try:
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        await db.rollback()
        raise already_exists("Username")
    except Exception:
        await db.rollback()
        raise internal_error()
    return success_message("updated", db_user.username)


@user.delete(
    "/users/{user_id}", 
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Delete a user",
    description="Deletes a user by ID and returns a status message.",
    tags=["User"],
)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    
    db_user = await db.get(User, user_id)
    
    if db_user is None:
        raise not_found("User")
    
    username = db_user.username  # Save before deletion
    try:
        await db.delete(db_user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise internal_error()
    return success_message("deleted", username)