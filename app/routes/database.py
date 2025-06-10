from fastapi import APIRouter
from app.database import reset_database

database = APIRouter()

@database.post(
    "/db/reset-db",
    summary="Reset the database",
    description="Drops and recreates all tables.",
    tags=["DEV"],
    )
async def reset_db():
    await reset_database()
    return {"message": "Database reset successful"}