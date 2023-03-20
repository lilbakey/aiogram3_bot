from models.data_base import async_db_session, BaseModel
from models.AdminModel import AdminModel

from sqlalchemy import (Column, Integer, String)
from sqlalchemy import (select, delete as sqlalchemy_delete)
from sqlalchemy.orm import Mapped


class Help(BaseModel, AdminModel):
    __tablename__ = 'helps'

    id: Mapped[int] = Column(Integer, primary_key=True)

    help_content: Mapped[String] = Column(String, nullable=False)

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