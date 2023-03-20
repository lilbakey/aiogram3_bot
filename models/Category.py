from typing import List

from models.data_base import async_db_session, BaseModel
from models.AdminModel import AdminModel

from sqlalchemy import (Column, Integer, VARCHAR)
from sqlalchemy import select
from sqlalchemy.orm import (relationship, Mapped)


class Category(BaseModel, AdminModel):
    __tablename__: str = "categories"

    # ID категории
    id: Column = Column(Integer, nullable=False, unique=True, primary_key=True)

    # Название категории
    name: Column = Column(VARCHAR(50), nullable=False, unique=True)

    # ID продуктов в категории
    product_id: Mapped[List["Product"]] = relationship(backref='category', cascade='all, delete')

    catalog_photo: Column = Column(VARCHAR(255), nullable=True, unique=False)

    @classmethod
    async def get_category_id(cls, name: str) -> str:
        query = (select(cls.id).where(cls.name == name))
        cat_id = await async_db_session.execute(query)
        cat_id = cat_id.scalars().first()

        return cat_id

    @classmethod
    async def get_exists(cls, ids: list) -> list:
        query = (select(cls.name).where(cls.id.in_(ids)))
        names = await async_db_session.execute(query)
        names = names.scalars().all()

        return names

    @classmethod
    async def check_name_in_base(cls, name: str) -> bool:
        query = select(cls.name)
        categories = await async_db_session.execute(query)
        categories = categories.scalars().all()

        return name in categories

    # @classmethod
    # async def get_names_categories(cls) -> list:
    #     query_name = select(cls.name)
    #     names = await async_db_session.execute(query_name)
    #     names = names.scalars().all()
    #
    #     return names

    def __repr__(self) -> str:
        return f'Category: \n' \
               f'ID: {self.id}\n' \
               f'Name: {self.name}\n' \
               f'Product ID: {self.product_id}'
