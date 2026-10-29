import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

import bcrypt


def get_password_hash(password: str) -> str:
    # Генерируем соль и хэшируем пароль (bcrypt работает только с байтами)
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    # Возвращаем строку для сохранения в БД
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    # Токен будет жить 30 минут (берем из настроек)
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Шифруем данные с помощью секретного ключа
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt