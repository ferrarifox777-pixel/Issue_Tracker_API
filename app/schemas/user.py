from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str

    # Эта настройка позволяет Pydantic читать данные из ORM-модели SQLAlchemy
    model_config = ConfigDict(from_attributes=True)