from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, schemas
from app.database import get_db

# Создаем роутер. prefix="/recipes" добавит этот путь ко всем эндпоинтам в файле
router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]  # Это сгруппирует методы в Swagger для фронтендеров
)

@router.get('/', 
            response_model=List[schemas.RecipeShort], 
            summary="Список всех рецептов")
async def read_recipes(db: AsyncSession = Depends(get_db)):
    """
    Первый экран: список рецептов с сортировкой по популярности и времени.
    """
    return await crud.get_all_recipes(db)


@router.get('/{recipe_id}', 
            response_model=schemas.RecipeDetail,
            summary="Детальная информация о рецепте",
            responses={
            404: {"description": "Рецепт не найден", "content": 
                    {"application/json": 
                        {"example": 
                            {"detail": "Рецепт не найден"}
                        }
                    }
                 }
            }
            )
async def read_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    """
    Второй экран: детальный рецепт. При каждом вызове увеличивает счетчик просмотров.
    """
    recipe = await crud.get_recipe_with_update_views(db, recipe_id)

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Рецепт не найден"
        )

    return recipe

@router.post('/',
             response_model=schemas.RecipeDetail,
             summary="Создание рецепта",
             status_code=201,
             responses={
            422: {"description": "Ошибка валидации данных"}
            }
            )
async def create_new_recipe(recipe: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)):
    """
    Создание нового рецепта.
    """
    return await crud.create_recipe(db, recipe)
