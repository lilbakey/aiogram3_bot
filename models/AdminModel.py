from typing import Optional

from sqlalchemy import (Select, Row)
from sqlalchemy import (update as sqlalchemy_update, select, delete as sqlalchemy_delete, insert as sqlalchemy_insert)
from sqlalchemy.engine.result import Result

from models.data_base import async_db_session

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

















