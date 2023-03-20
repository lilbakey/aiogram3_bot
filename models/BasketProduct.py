from models.data_base import async_db_session, BaseModel
from models.AdminModel import AdminModel

from sqlalchemy import (Column, Integer, ForeignKey)
from sqlalchemy import (select, delete as sqlalchemy_delete)
from sqlalchemy.orm import (relationship, selectinload, Mapped)


class BasketProduct(BaseModel, AdminModel):
    __tablename__: str = 'basket_product'

    id: Mapped[int] = Column(Integer, nullable=False, unique=True, primary_key=True)

    basket_id: Mapped[int] = Column(Integer, ForeignKey('baskets.id', ondelete='CASCADE'))

    basket: Mapped["Basket"] = relationship(back_populates='products', cascade='all, delete', lazy=True)

    product_id: Mapped[int] = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'))

    product: Mapped["Product"] = relationship(back_populates='baskets', cascade='all, delete', lazy=True)

    __mapper_args__: dict[str, bool] = {"eager_defaults": True}

    @classmethod
    async def clear_basket(cls, basket_id: int) -> None:
        query = sqlalchemy_delete(cls).where(cls.basket_id == basket_id)
        await async_db_session.execute(query)

        try:
            await async_db_session.commit()
        except Exception:
            await async_db_session.rollback()
            raise

    @classmethod
    async def get_object(cls, id: int):
        query = select(cls).where(cls.id == id).options(selectinload(cls.product))
        obj = await async_db_session.execute(query)
        obj = obj.scalars().first()

        return obj

    @classmethod
    async def get_id(cls, product_id: int) -> int:
        query = select(cls.id).where(cls.product_id == product_id)
        id = await async_db_session.execute(query)
        id = id.scalars().first()

        return id
    def __repr__(self) -> str:
        return f'BasketProduct:\n' \
               f'basket_id: {self.basket_id}\n' \
               f'product_id: {self.product_id}\n'