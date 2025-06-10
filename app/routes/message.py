from fastapi import APIRouter, Depends, status
from sqlalchemy import select, desc
from app.models import Message, Category, User
from app.schema import MessageBase, SuccessResponse, ErrorResponse
from app.responses import success_message, internal_error, not_found
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

message = APIRouter()

@message.post(
    "/messages", 
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Create a new message",
    description="Creates a message and returns the message if successful.",
    tags=["Message"],
)
async def create_message(message_in: MessageBase, db: AsyncSession = Depends(get_db)):
    db_category = await db.get(Category, message_in.category_id)
    db_user = await db.get(User, message_in.user_id)
    
    if db_category is None and db_user is None:
        raise not_found("User and Category")
    
    elif db_user is None:
        raise not_found("User")
    
    elif db_category is None:
        raise not_found("Category")
    
    else:
        new_message = Message(
        user_id = message_in.user_id,
        message = message_in.message,
        category_id = message_in.category_id
        )   
    
        db.add(new_message)
        try:
            await db.commit()
            await db.refresh(new_message)
        except Exception:
            await db.rollback()
            raise internal_error()
        return success_message("added", message_in.message)
    

@message.get(
    "/messages/{message_id}",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        },
    summary="Retrieve a message by ID",
    description="Fetches a message by their unique ID and returns their details if found.",
    tags=["Message"],
)
async def get_message(message_id: int, db: AsyncSession = Depends(get_db)):
    message = await db.get(Message, message_id)

    if message is None:
        raise not_found("Message")
    return message


@message.get(
    "/messages",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": MessageBase, "description": "List of users"},
        404: {"model": SuccessResponse, "description": "No users found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Get all messages",
    description="Retrieves all messages. Returns a message if no messages are found.",
    tags=["Message"],
)
async def get_messages(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Message).order_by(desc(Message.id)))
    messages = result.all()

    if not messages:
        return {'message': 'No messages found'}
    return messages


@message.delete(
    "/messages/{user_id}", 
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Message not found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Delete a message",
    description="Deletes a message by ID and returns a status message.",
    tags=["Message"],
)
async def delete_user(message_id: int, db: AsyncSession = Depends(get_db)):
    
    db_message = await db.get(Message, message_id)
    
    if db_message is None:
        raise not_found("Message")
    
    message = db_message.message  # Save before deletion
    try:
        await db.delete(db_message)
        await db.commit()
    except Exception:
        await db.rollback()
        raise internal_error()
    return success_message("deleted", "Message")