from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    old_password: Optional[str] = None

class UserInDBBase(BaseModel):
    user_id: int
    username: str
    email: str
    is_active: bool
    tenant_id: int

    class Config:
        from_attributes = True
