from pydantic import BaseModel, ConfigDict, constr

UsernameStr = constr(min_length=1)

class UserBase(BaseModel):
    username: UsernameStr #type: ignore

    model_config = ConfigDict(from_attributes=True) 

class UserRead(BaseModel):
    id: int
    username: str

class CategoryBase(BaseModel):
    category_name: str

    model_config = ConfigDict(from_attributes=True) 

class SuccessResponse(BaseModel):
    message: str
    data: str

class ErrorResponse(BaseModel):
    detail: str