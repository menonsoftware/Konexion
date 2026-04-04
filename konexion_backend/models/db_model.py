from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Base class for declarative models
Base = declarative_base()


class Database:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=True)
        self.SessionLocal = async_sessionmaker(bind=self.engine, expire_on_commit=False)

    async def get_session(self) -> AsyncSession:
        async with self.SessionLocal() as session:
            yield session

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


databse_url = "sqlite+aiosqlite:///./konexion.db"
database = Database(databse_url)
