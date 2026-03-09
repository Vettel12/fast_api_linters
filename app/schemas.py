from pydantic import BaseModel, ConfigDict, Field


class RecipeShort(BaseModel):
    title: str = Field(..., description="Название блюда", examples=["Омлет"])
    cooking_time: int = Field(
        ..., description="Время приготовления в минутах", examples=[10]
    )
    views_count: int = Field(
        ..., description="Количество просмотров рецепта", examples=[100]
    )

    model_config = ConfigDict(
        from_attributes=True
    )  # Позволяет Pydantic работать с объектами SQLAlchemy (Row)


class RecipeDetail(BaseModel):
    id: int = Field(..., description="Уникальный ID рецепта")
    title: str = Field(..., description="Название блюда")
    cooking_time: int = Field(..., description="Время в минутах")
    ingredients: str = Field(..., description="Список ингредиентов строкой")
    description: str = Field(..., description="Текстовое описание процесса")
    views_count: int = Field(
        ..., description="Количество просмотров рецепта", examples=[100]
    )

    model_config = ConfigDict(from_attributes=True)


class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    cooking_time: int = Field(..., gt=0)  # Время должно быть больше 0
    ingredients: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
