from typing import List, Union

from models.data_base import async_db_session, BaseModel
from models.AdminModel import AdminModel

from sqlalchemy import (Column, Integer, VARCHAR, ForeignKey)
from sqlalchemy import select
from sqlalchemy.orm import (relationship, selectinload, Mapped)


class Product(BaseModel, AdminModel):
    __tablename__: str = "products"

    # Уникальный ID товара
    id: Column = Column(Integer, nullable=False, unique=True, primary_key=True)

    # Фотография товара
    photo: Column = Column(VARCHAR(255), nullable=False, unique=False)

    # Название товара
    name: Column = Column(VARCHAR(100), nullable=False, unique=False)

    # Описание товара
    description: Column = Column(VARCHAR(255), nullable=False, unique=False)

    # Цена товара
    price: Column = Column(Integer, nullable=False, unique=False)

    category_id: Mapped[int] = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)

    baskets: Mapped[List["BasketProduct"]] = relationship(back_populates='product', cascade='all, delete')

    __mapper_args__: dict[str, bool] = {"eager_defaults": True}

    @classmethod
    async def get_object(cls, id: int):
        query = select(cls).where(cls.id == id).options(selectinload(cls.baskets))
        obj = await async_db_session.execute(query)
        obj = obj.scalars().first()

        return obj

    @classmethod
    async def get_products_in_category(cls, category_id) -> list[dict[str, Union[str, int]]]:
        query = select(cls).where(cls.category_id == category_id)
        products = await async_db_session.execute(query)
        products = [{'id': i.id, 'photo': i.photo, 'name': i.name, 'descr': i.description, 'price': i.price} for i in
                    products.scalars().all()]

        return products

    @classmethod
    async def get_product_id(cls, name: str) -> str:
        query = (select(cls.id).where(cls.name == name))
        cat_id = await async_db_session.execute(query)
        cat_id = cat_id.scalars().first()

        return cat_id

    @classmethod
    async def get_exists_categories(cls) -> list:
        query = (select(cls.category_id)).distinct()
        ids = await async_db_session.execute(query)
        ids = ids.scalars().all()

        return ids

    def __repr__(self) -> str:
        return f'Product: \n' \
               f'ID: {self.id}\n' \
               f'Photo: {self.photo}\n' \
               f'Name: {self.name}\n' \
               f'Description: {self.description}\n' \
               f'Price: {self.price}\n'
