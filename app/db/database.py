from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Создаем асинхронный движок. echo=True будет выводить SQL-запросы в консоль (полезно при разработке)
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Фабрика сессий
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Зависимость (Dependency) для FastAPI
async def get_async_session():
    async with async_session_maker() as session:
        yield session
