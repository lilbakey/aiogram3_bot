from typing import List

from models.data_base import async_db_session, BaseModel
from models.AdminModel import AdminModel

from sqlalchemy import (Column, Integer, ForeignKey)
from sqlalchemy import select
from sqlalchemy.orm import (relationship, selectinload, Mapped)

class Basket(BaseModel, AdminModel):
    __tablename__: str = 'baskets'

    # ID покупки
    id: Column = Column(Integer, nullable=False, unique=True, primary_key=True)

    # ID покупателя
    users_telegram_id: Column = Column(Integer, ForeignKey('users.telegram_id', ondelete='CASCADE'), nullable=False)

    user: Mapped["User"] = relationship(back_populates='basket', cascade='all, delete')

    # ID товара
    products: Mapped[List["BasketProduct"]] = relationship(back_populates='basket', cascade='all, delete')

    __mapper_args__: dict[str, bool] = {"eager_defaults": True}


    @classmethod
    async def get_basket(cls, telegram_id: int):
        query = select(cls).where(cls.users_telegram_id == telegram_id).options(selectinload(cls.products))
        basket = await async_db_session.execute(query)
        products = basket.scalars().first()

        return products

    @classmethod
    async def get_id(cls, telegram_id: int) -> int:
        query = select(cls.id).where(cls.users_telegram_id == telegram_id)
        basket_id = await async_db_session.execute(query)
        basket_id = basket_id.scalars().first()

        return basket_id

    def __repr__(self) -> str:
        return f'Basket: \n' \
               f'ID: {self.id}\n' \
               f'User_telegram_id: {self.users_telegram_id}\n' \
               f'Products: {self.products}'