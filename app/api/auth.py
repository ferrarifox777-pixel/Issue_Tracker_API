from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_async_session
from app.models.user import User
from app.core.security import verify_password, create_access_token

router = APIRouter(tags=["Auth"])


# Используем стандартный класс FastAPI для принятия формы с логином (username) и паролем
@router.post("/login")
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    # 1. Ищем пользователя (в OAuth2 поле логина всегда называется username, мы передадим туда email)
    query = select(User).where(User.email == form_data.username)
    result = await session.execute(query)
    user = result.scalars().first()

    # 2. Проверяем существование пользователя и правильность пароля
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Генерируем токен, зашивая в него ID пользователя
    access_token = create_access_token(data={"sub": str(user.id)})

    # 4. Возвращаем ответ в стандартном для OAuth2 формате
    return {"access_token": access_token, "token_type": "bearer"}