from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_async_session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, session: AsyncSession = Depends(get_async_session)):
    # 1. Проверяем, существует ли уже пользователь с таким email
    query = select(User).where(User.email == user_in.email)
    result = await session.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    # 2. Хэшируем пароль и создаем объект пользователя
    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(email=user_in.email, hashed_password=hashed_pwd)

    # 3. Сохраняем в базу данных
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)  # Обновляем объект, чтобы получить ID из базы

    # 4. Возвращаем данные (Pydantic автоматически отфильтрует пароль согласно UserResponse)
    return new_user


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Получить данные своего профиля. Доступно только авторизованным."""
    return current_user