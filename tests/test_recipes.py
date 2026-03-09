from typing import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.database import Base, engine
from app.main import app

# --- Фикстуры инфраструктуры ---

@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"

@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    """Создаем схему БД один раз на всю сессию."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(autouse=True)
async def clear_tables():
    """Очищаем данные во всех таблицах после каждого теста для изоляции."""
    yield
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

@pytest.fixture
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """Универсальный клиент для выполнения запросов."""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        yield client

# --- Тесты ---

async def test_create_recipe(ac: AsyncClient):
    """Проверяем успешное создание рецепта."""
    response = await ac.post(
        "/recipes/",
        json={
            "title": "Тестовый салат",
            "cooking_time": 10,
            "ingredients": "Зелень, масло",
            "description": "Просто нарежьте всё",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Тестовый салат"
    assert "id" in data

async def test_get_all_recipes(ac: AsyncClient):
    """Проверяем получение списка рецептов."""
    # Создаем один рецепт, чтобы список не был пустым
    await ac.post("/recipes/", json={
        "title": "Хлеб", "cooking_time": 1, "ingredients": "Мука", "description": "Печь"
    })
    
    response = await ac.get("/recipes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1

async def test_recipe_views_increment(ac: AsyncClient):
    """Проверяем счетчик просмотров."""
    # 1. Создаем
    create_resp = await ac.post(
        "/recipes/",
        json={
            "title": "Утренний кофе",
            "cooking_time": 5,
            "ingredients": "Кофе",
            "description": "Варить",
        },
    )
    recipe_id = create_resp.json()["id"]

    # 2. Первый просмотр
    res1 = await ac.get(f"/recipes/{recipe_id}")
    assert res1.json()["views_count"] == 1

    # 3. Второй просмотр
    res2 = await ac.get(f"/recipes/{recipe_id}")
    assert res2.json()["views_count"] == 2

async def test_create_recipe_validation_error(ac: AsyncClient):
    """Проверяем ошибку валидации (422)."""
    response = await ac.post(
        "/recipes/",
        json={
            "title": "Сломанный рецепт",
            "cooking_time": "десять минут",  # Ошибка типа
            "ingredients": "Соль",
            "description": "...",
        },
    )
    assert response.status_code == 422
    assert "detail" in response.json()
