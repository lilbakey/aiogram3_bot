from models.data_base import async_db_session, BaseModel
from models.AdminModel import AdminModel

from sqlalchemy import (Column, Integer, String)
from sqlalchemy import (select, delete as sqlalchemy_delete)
from sqlalchemy.orm import Mapped


class FAQ(BaseModel, AdminModel):
    __tablename__: str = 'FAQs'

    id: Mapped[int] = Column(Integer, primary_key=True)

    faq_content: Mapped[String] = Column(String, nullable=False)

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
