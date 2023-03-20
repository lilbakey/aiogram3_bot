from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession, create_async_engine as _create_async_engine)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config_data.config import Config, load_config

config: Config = load_config('.env')

BaseModel: declarative_base = declarative_base()


class AsyncDatabaseSession:
    def __init__(self):
        self._session: sessionmaker[AsyncSession] | None = None
        self._engine: AsyncEngine | None = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    async def init(self):
        self._engine: AsyncEngine = _create_async_engine(URL.create(
            drivername='postgresql+asyncpg',
            username=config.db.db_user,
            password=config.db.db_password,
            host=config.db.db_host,
            port=config.db.db_port,
            database=config.db.database
        ), echo=True)
        self._session: sessionmaker[AsyncSession] = sessionmaker(self._engine, expire_on_commit=False,
                                                                 class_=AsyncSession)()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)


async_db_session = AsyncDatabaseSession()
