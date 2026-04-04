from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


# Base class for declarative models — uses the SQLAlchemy 2.x class-based API
# so that mypy can resolve it as an actual type rather than a runtime value.
class Base(DeclarativeBase):  # type: ignore[misc]
    pass


class Database:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=True)
        self.SessionLocal = async_sessionmaker(bind=self.engine, expire_on_commit=False)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.SessionLocal() as session:
            yield session

    async def init_db(self):
        # Import all models so Base.metadata knows about every table
        import konexion_backend.models.user_model  # noqa: F401

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


def _build_database_url() -> str:
    """Read database URL from config, falling back to SQLite."""
    try:
        from konexion_backend.config import get_database_config

        url = get_database_config().url
        if url:
            return url
    except Exception:  # nosec B110
        pass
    return "sqlite+aiosqlite:///./konexion.db"


database_url = _build_database_url()
database = Database(database_url)
