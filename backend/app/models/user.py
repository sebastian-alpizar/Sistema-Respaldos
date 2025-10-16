from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    DBA = "dba"
    VIEWER = "viewer"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.DBA
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    created_at: str