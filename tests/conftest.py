import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.db.database import get_async_session
from app.models.base import Base
from app.core.config import settings

# URL тестовой БД (меняем только имя базы в конце)
TEST_DB_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/tracker_test_db"

engine_test = create_async_engine(TEST_DB_URL, echo=False)
test_session_maker = async_sessionmaker(engine_test, expire_on_commit=False)

# Функция, которая подменит боевую сессию на тестовую
async def override_get_async_session():
    async with test_session_maker() as session:
        yield session

# Указываем FastAPI использовать подмену
app.dependency_overrides[get_async_session] = override_get_async_session

# Фикстура, которая создает таблицы перед запуском всех тестов и удаляет их после
@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Фикстура для имитации HTTP-запросов к нашему API
@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac