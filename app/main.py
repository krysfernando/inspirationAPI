from fastapi import FastAPI
from app.routes import (
    user as user_route,
    database as db_route,
    category as category_route,
    message as message_route
    )

app = FastAPI()

app.include_router(db_route.database)
app.include_router(user_route.user)
app.include_router(category_route.category)
app.include_router(message_route.message)