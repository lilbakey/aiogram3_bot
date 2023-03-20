import datetime
from typing import Optional

from models.data_base import async_db_session, BaseModel
from models.AdminModel import AdminModel

from sqlalchemy import (Column, Integer, VARCHAR, DATE, Select, String)
from sqlalchemy import (select, update as sqlalchemy_update)
from sqlalchemy.orm import (relationship, Mapped)


class User(BaseModel, AdminModel):
    __tablename__ = 'users'

    # ID пользователя
    id: Mapped[int] = Column(Integer, unique=True, nullable=False, primary_key=True)

    # ID пользователя телеграм
    telegram_id: Mapped[int] = Column(Integer, unique=True, nullable=False)

    # Телеграм username
    username: Mapped[str] = Column(VARCHAR(32), unique=False, nullable=True)

    # Баланс пользователя
    balance: Mapped[int] = Column(Integer, unique=False, nullable=True)

    # Дата регистрации
    reg_date: Mapped[int] = Column(DATE, default=datetime.date.today())

    referrer_link: Mapped[str] = Column(String, unique=True, nullable=False)

    referrer_counter: Mapped[int] = Column(Integer, unique=False, nullable=False)

    buy_counter: Mapped[int] = Column(Integer, unique=False, nullable=False)

    basket: Mapped["Basket"] = relationship(back_populates='user', uselist=False, cascade='all, delete')

    def __init__(self, telegram_id: Mapped[int], username: Mapped[str], referrer_link: Mapped[str],
                 balance: Mapped[int] = 0, referrer_counter: Mapped[int] = 0, buy_counter: Mapped[int] = 0) -> None:
        self.telegram_id = telegram_id
        self.username = username
        self.balance = balance
        self.referrer_link = referrer_link
        self.referrer_counter = referrer_counter
        self.buy_counter = buy_counter

    @classmethod
    async def create_user(cls, telegram_id: Mapped[int], username: Mapped[str], referrer_link: Mapped[str],
                          balance: Mapped[int] = 0, referrer_counter: Mapped[int] = 0, buy_counter: Mapped[int] = 0):
        table = cls(telegram_id=telegram_id,
                    username=username,
                    balance=balance,
                    referrer_link=referrer_link,
                    referrer_counter=referrer_counter,
                    buy_counter=buy_counter)

        async_db_session.add(table)

        try:
            await async_db_session.commit()
        except Exception:
            await async_db_session.rollback()
            raise

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
               f'Registration_date: {self.reg_date}\n'
