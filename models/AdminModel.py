import datetime

from typing import Optional, List

from sqlalchemy import (Column, Integer, VARCHAR, DATE, ForeignKey, Select, Row, Table, String)
from sqlalchemy import (update as sqlalchemy_update, select, delete as sqlalchemy_delete, insert as sqlalchemy_insert)
from sqlalchemy.orm import (relationship, selectinload, Mapped)
from sqlalchemy.engine.result import Result

from models.data_base import async_db_session, BaseModel


class AdminModel:

    @classmethod
    async def insert(cls, **kwargs: str | int):
        table = cls(**kwargs)
        query = (
            sqlalchemy_insert(cls)
            .values(**kwargs)
            .execution_options(synchronize_session='fetch')
        )

        await async_db_session.execute(query)

        try:
            await async_db_session.commit()
        except Exception:
            await async_db_session.rollback()
            raise

        return table

    @classmethod
    async def create(cls, **kwargs: str | int):
        table = cls(**kwargs)
        async_db_session.add(table)

        try:
            await async_db_session.commit()
        except Exception:
            await async_db_session.rollback()
            raise

        return table

    @classmethod
    async def update(cls, id: int, **kwargs: str | int):
        query = (
            sqlalchemy_update(cls)
            .where(cls.id == id)
            .values(**kwargs)
            .execution_options(synchronize_session='fetch')
        )

        await async_db_session.execute(query)

        try:
            await async_db_session.commit()
        except Exception:
            await async_db_session.rollback()
            raise

        return await cls.get(id)



    @classmethod
    async def get(cls, id: int) -> Optional[Row]:
        query: Select = select(cls.id).where(cls.id == id)
        rows: Result = await async_db_session.execute(query)
        row: Optional[Row] = rows.first()

        return row

    @classmethod
    async def get_all(cls) -> list:
        query: Select = select(cls)
        rows = await async_db_session.execute(query)
        rows = rows.scalars().all()

        return rows

    @classmethod
    async def delete(cls, id: int) -> bool:
        query = sqlalchemy_delete(cls).where(cls.id == id)
        await async_db_session.execute(query)

        try:
            await async_db_session.commit()
        except Exception:
            await async_db_session.rollback()
            raise

        return True


class User(BaseModel, AdminModel):
    __tablename__ = 'users'

    # ID пользователя
    id: Column = Column(Integer, unique=True, nullable=False, primary_key=True)

    # ID пользователя телеграм
    telegram_id: Column = Column(Integer, unique=True, nullable=False)

    # Телеграм username
    username: Column = Column(VARCHAR(32), unique=False, nullable=True)

    # Баланс пользователя
    balance: Column = Column(Integer, unique=False, nullable=True)

    # Дата регистрации
    reg_date: Column = Column(DATE, default=datetime.date.today())

    basket: Mapped["Basket"] = relationship(back_populates='user', uselist=False, cascade='all, delete')

    @classmethod
    async def check_user_in_base(cls, telegram_id: int) -> bool:
        query: Select = (
            select(cls.telegram_id)
            .where(cls.telegram_id == telegram_id))

        rows = await async_db_session.execute(query)
        rows = rows.scalars().all()

        return telegram_id in rows

    @classmethod
    async def get_user(cls, telegram_id: int):
        query = select(cls).where(cls.telegram_id == telegram_id)
        obj = await async_db_session.execute(query)
        obj = obj.scalars().first()

        return obj

    def __repr__(self) -> str:
        return f'User: \n' \
               f'ID: {self.id}\n' \
               f'Telegram_id: {self.telegram_id}\n' \
               f'Username: {self.username}\n' \
               f'Balance: {self.balance}\n' \
               f'Registration_date: {self.reg_date}\n' \

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

    @classmethod
    async def get_names_categories(cls) -> list:
        query_name = select(cls.name)
        names = await async_db_session.execute(query_name)
        names = names.scalars().all()

        return names

    def __repr__(self) -> str:
        return f'Category: \n' \
               f'ID: {self.id}\n' \
               f'Name: {self.name}\n' \
               f'Product ID: {self.product_id}'


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
    async def get_products_in_category(cls, category_id) -> list[dict]:
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

class BasketProduct(BaseModel, AdminModel):
    __tablename__: str = 'basket_product'

    id: Mapped[int] = Column(Integer, nullable=False, unique=True, primary_key=True)

    basket_id: Mapped[int] = Column(Integer, ForeignKey('baskets.id', ondelete='CASCADE'))

    basket: Mapped["Basket"] = relationship(back_populates='products', cascade='all, delete', lazy=True)

    product_id: Mapped[int] = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'))

    product: Mapped["Product"] = relationship(back_populates='baskets', cascade='all, delete', lazy=True)

    __mapper_args__: dict[str, bool] = {"eager_defaults": True}

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


class Help(BaseModel, AdminModel):
    __tablename__ = 'helps'

    id: Column = Column(Integer, primary_key=True)

    help_content: Column = Column(String, nullable=False)

    @classmethod
    async def get_help_content(cls) -> str:
        query = select(cls.help_content)
        text_help = await async_db_session.execute(query)
        text_help = text_help.scalars().first()

        return text_help

    @classmethod
    async def delete_help_content(cls) -> None:
        query = sqlalchemy_delete(cls)
        await async_db_session.execute(query)

        try:
            await async_db_session.commit()
        except Exception:
            await async_db_session.rollback()
            raise

class FAQ(BaseModel, AdminModel):
    __tablename__: str = 'FAQs'

    id: Column = Column(Integer, primary_key=True)

    faq_content: Column = Column(String, nullable=False)

    @classmethod
    async def get_faq_content(cls) -> str:
        query = select(cls.faq_content)
        faq_text = await async_db_session.execute(query)
        faq_text = faq_text.scalars().first()

        return faq_text

    @classmethod
    async def delete_faq_content(cls) -> None:
        query = sqlalchemy_delete(cls)
        await async_db_session.execute(query)

        try:
            await async_db_session.commit()
        except Exception:
            await async_db_session.rollback()
            raise
