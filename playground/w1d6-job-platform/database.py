from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from sqlmodel import SQLModel

from models.application import Application
from models.member import Member
from models.company import Company
from models.job_post import JobPost
from models.job_post_tag import JobPostTag
from models.tag import Tag

engine: AsyncEngine = create_async_engine(
    "sqlite+aiosqlite:///./database.db",
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def create_tables() -> None:
    """앱 시작 시 DB 스키마 생성 (없을 때만)"""
    _ = (Member, Company, JobPost, Tag, JobPostTag, Application)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db_connections() -> None:
    """앱 종료 시 DB 연결 풀을 정리합니다."""
    await engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """라우터에서 DB 세션을 주입받기 위한 의존성 함수"""
    async with async_session_factory() as session:
        yield session
