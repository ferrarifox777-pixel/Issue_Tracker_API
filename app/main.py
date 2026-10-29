from fastapi import FastAPI
from app.api.users import router as users_router # <-- Добавили импорт
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router # <-- Добавили

app = FastAPI(
    title="Issue Tracker API",
    description="API для управления задачами",
    version="1.0.0"
)

app.include_router(users_router) # <-- Подключили роутер
app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/ping", tags=["Healthcheck"])
async def ping():
    return {"status": "ok", "message": "Pong!"}