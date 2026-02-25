import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import Base, engine

# 1. Настройка тестовой базы данных (Fixtures)
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    """Создаем таблицы перед тестами и удаляем после."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 2. Тест создания рецепта (POST /recipes)
@pytest.mark.asyncio
async def test_create_recipe():
    """
    Проверяем, что рецепт успешно создается и 
    возвращается корректный JSON с ID.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/recipes/", json={
            "title": "Тестовый салат",
            "cooking_time": 10,
            "ingredients": "Зелень, масло",
            "description": "Просто нарежьте всё"
        })
    assert response.status_code == 201
    assert response.json()["title"] == "Тестовый салат"
    assert "id" in response.json()

# 3. Тест получения списка (GET /recipes)
@pytest.mark.asyncio
async def test_get_all_recipes():
    """
    Проверяем, что эндпоинт отдает список.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/recipes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 4. Тест инкремента просмотров (GET /recipes/{id})
@pytest.mark.asyncio
async def test_recipe_views_increment():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Создаем рецепт и получаем его реальные данные
        create_resp = await ac.post("/recipes/", json={
            "title": "Утренний кофе",
            "cooking_time": 5,
            "ingredients": "Кофе, вода",
            "description": "Сварить в турке"
        })
        # Проверяем, что создание прошло успешно
        assert create_resp.status_code == 201
        recipe_id = create_resp.json()["id"]

        # 2. Делаем ПЕРВЫЙ просмотр
        response1 = await ac.get(f"/recipes/{recipe_id}")
        assert response1.status_code == 200
        assert response1.json()["views_count"] == 1

        # 3. Делаем ВТОРОЙ просмотр
        response2 = await ac.get(f"/recipes/{recipe_id}")
        assert response2.status_code == 200
        assert response2.json()["views_count"] == 2

@pytest.mark.asyncio
async def test_create_recipe_validation_error():
    """
    Проверяем, что при отправке некорректных данных (строка вместо числа)
    FastAPI возвращает 422 Unprocessable Entity.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/recipes/", json={
            "title": "Сломанный рецепт",
            "cooking_time": "десять минут",  # ОШИБКА: должно быть int
            "ingredients": "Соль",
            "description": "..."
        })
    
    assert response.status_code == 422
    # Проверяем, что в ответе есть описание ошибки валидации
    assert "detail" in response.json()
