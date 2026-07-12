from ninja import Schema
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ==================== AUTH SCHEMAS ====================
class RegisterSchema(Schema):
    username: str
    email: str
    password: str
    role: str = "student" # Default role jika tidak diisi

class LoginSchema(Schema):
    username: str
    password: str

class TokenSchema(Schema):
    access_token: str
    refresh_token: str

class UserOutSchema(Schema):
    id: int
    username: str
    email: str
    role: str

# ==================== COURSE SCHEMAS ====================
class CourseIn(Schema):
    name: str
    description: str = '-'
    price: int = 10000

class CourseOut(Schema):
    id: int
    name: str
    description: str
    price: int
    teacher: UserOutSchema
    created_at: datetime
    updated_at: datetime