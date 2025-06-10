from fastapi import status, HTTPException

# Success responses (as dicts)
def success_message(action: str, resource: str):
    return {"message": f"{resource} {action} successfully"}

# Error responses (as HTTPException factories)
def already_exists(resource: str):
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{resource} already exists"
    )

def not_found(resource: str):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found"
    )

def bad_request(reason: str = "Bad request"):
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=reason
    )

def internal_error(detail: str = "Internal server error"):
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail
    )