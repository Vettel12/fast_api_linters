from typing import Any, Optional, Sequence

from sqlalchemy import Row, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models, schemas


# 1. Получить список всех рецептов (первый экран)
async def get_all_recipes(db: AsyncSession) -> Sequence[Row[Any]]:
    """
    Возвращает список строк (Row), содержащих только выбранные поля.

    SELECT id, title, views_count, cooking_time
    FROM recipes
    ORDER BY views_count DESC, cooking_time ASC;
    """
    result = await db.execute(
        select(
            models.Recipe.id,
            models.Recipe.title,
            models.Recipe.views_count,
            models.Recipe.cooking_time,
        ).order_by(models.Recipe.views_count.desc(), models.Recipe.cooking_time.asc())
    )

    return result.all()


# 2. Получить один рецепт + обновить просмотры (второй экран)
async def get_recipe_with_update_views(
    db: AsyncSession, recipe_id: int
) -> Optional[Row[Any]]:
    """
    UPDATE recipes
    SET views_count = views_count + 1
    WHERE id = :recipe_id;

    SELECT id, title, cooking_time, ingredients, description
    FROM recipes
    WHERE id = :recipe_id;
    """
    # Сначала увеличиваем счетчик
    await db.execute(
        update(models.Recipe)
        .where(models.Recipe.id == recipe_id)
        .values(views_count=models.Recipe.views_count + 1)
    )
    await db.commit()

    # Затем получаем детальную информацию
    result = await db.execute(
        select(
            models.Recipe.id,
            models.Recipe.title,
            models.Recipe.cooking_time,
            models.Recipe.ingredients,
            models.Recipe.description,
            models.Recipe.views_count,
        ).where(models.Recipe.id == recipe_id)
    )

    return result.first()


# 3. Создать новый рецепт
async def create_recipe(
    db: AsyncSession, recipe: schemas.RecipeCreate
) -> models.Recipe:
    """
    INSERT INTO recipes (title, cooking_time, ingredients, description, views_count)
    VALUES (:title, :cooking_time, :ingredients, :description, 0)
    RETURNING id, title, cooking_time, ingredients, description, views_count;
    """
    new_recipe = models.Recipe(
        title=recipe.title,
        cooking_time=recipe.cooking_time,
        ingredients=recipe.ingredients,
        description=recipe.description,
    )

    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)

    return new_recipe
