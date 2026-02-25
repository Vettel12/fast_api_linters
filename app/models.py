from sqlalchemy import Column, String, Integer

from app.database import Base


class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    cooking_time = Column(Integer, index=True)
    ingredients = Column(String)
    description = Column(String)
    views_count = Column(Integer, default=0, index=True)
