from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, desc
from app.models import Category
from app.schema import CategoryBase, SuccessResponse, ErrorResponse
from app.responses import success_message, already_exists, internal_error, not_found
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

category = APIRouter()

@category.post(
    "/categories",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        409: {"model": ErrorResponse, "description": "Category already exists"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Create a new category",
    description="Creates a category and returns the category if successful.",
    tags=["Category"],
)
async def create_category(category_in: CategoryBase, db: AsyncSession = Depends(get_db)):
    new_category = Category(
        category_name = (category_in.category_name).lower()
        )
    
    db.add(new_category)

    try:
        await db.commit()
        await db.refresh(new_category)
    except IntegrityError:
        await db.rollback()
        raise already_exists(category_in.category_name)
    except Exception:
        await db.rollback()
        raise internal_error()
    return success_message("created", new_category.category_name)


@category.get(
        "/categories/{category_id}", 
        status_code=status.HTTP_200_OK,
        responses={
            404: {"model": ErrorResponse, "description": "Category not found"},
            500: {"model": ErrorResponse, "description": "Internal Server Error"},
            },
        summary="Retrieve a Category by ID",
        description="Fetches a category by their unique ID and returns their details if found.",
        tags=["Category"],
)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await db.get(Category, category_id)

    if category is None:
        raise not_found("Category")
    return category


@category.get(
    "/categories",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": CategoryBase, "description": "List of categories"},
        404: {"model": SuccessResponse, "description": "No categoies found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Get all categories",
    description="Retrieves all categories. Returns a message if no categories are found.",
    tags=["Category"],
)
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Category).order_by(desc(Category.id)))
    categories = result.all()

    if not categories:
        return {'message': 'No categories found'}
    return categories


@category.patch(
    "/categories/{category_id}",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Category not found"},
        409: {"model": ErrorResponse, "description": "Category name already exists"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Update a category",
    description="Updates a category's name by ID and returns a status message.",
    tags=["Category"],
)
async def update_category(category_id: int, category: CategoryBase, db: AsyncSession = Depends(get_db)):
    db_category = await db.get(Category, category_id)
    
    if db_category is None:
        raise not_found("Category")
    
    db_category.category_name = category.category_name  # Only update allowed fields

    try:
        await db.commit()
        await db.refresh(db_category)
    except IntegrityError:
        await db.rollback()
        raise already_exists("Category name")
    except Exception:
        await db.rollback()
        raise internal_error()
    return success_message("updated", db_category.category_name)


@category.delete(
    "/categories/{category_id}", 
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Category not found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Delete a category",
    description="Deletes a category by ID and returns a status message.",
    tags=["Category"],
)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    db_category = await db.get(Category, category_id)

    if db_category is None:
        raise not_found("Category")
    
    category_name = db_category.category_name  # Save before deletion
    
    try:
        await db.delete(db_category)
        await db.commit()
    except Exception:
        await db.rollback()
        raise internal_error()
    return success_message("deleted", category_name)