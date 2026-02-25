from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import recipes
from app.database import engine, Base


# 1. Создаем функцию жизненного цикла (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код здесь выполнится ПРИ ЗАПУСКЕ приложения
    async with engine.begin() as conn:
        # Создаем таблицы, если их нет
        await conn.run_sync(Base.metadata.create_all)

    yield  # Здесь приложение "работает"

    # Код после yield выполнится ПРИ ВЫКЛЮЧЕНИИ приложения
    await engine.dispose() # Корректно закрываем все соединения с БД

# 2. Передаем lifespan в инициализацию FastAPI
app = FastAPI(
    title="API Кулинарной книги",
    description="Максимально полное описание бэкенда для фронтенд-разработчиков",
    version="1.0.0",
    lifespan=lifespan  # Подключаем наш менеджер жизненного цикла
)

# 3. Подключаем роутеры
app.include_router(recipes.router)

@app.get("/", tags=["Root"])
async def root():
    return {"message": "API работает. Документация на /docs"}