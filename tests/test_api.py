import pytest


async def test_ping(client):
    # Отправляем GET запрос
    response = await client.get("/ping")

    # Проверяем статус-код и тело ответа
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Pong!"}


async def test_register_user(client):
    # Отправляем POST запрос с JSON
    response = await client.post("/users/register", json={
        "email": "qa@example.com",
        "password": "super_secure_password"
    })

    # Убеждаемся, что юзер создан
    assert response.status_code == 201
    data = response.json()

    # Проверяем, что API вернуло правильный email, присвоило ID и НЕ вернуло пароль
    assert data["email"] == "qa@example.com"
    assert "id" in data
    assert "hashed_password" not in data