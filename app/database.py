from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from app.config import settings
from app.models.company import Company
from app.models.job_post import JobPost

# echo=True → 실행되는 SQL 쿼리를 터미널에 출력 (학습/디버깅용)
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=settings.db_pool_pre_ping,
)

async_session_factory = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def create_db_and_tables() -> None:
    """앱 시작 시 테이블 생성 (없을 때만)"""
    # Ensure models are imported before metadata.create_all runs.
    _ = (Company, JobPost)
    async with engine.begin() as conn:
        # create_all: 테이블이 없으면 생성해줍니다.
        # 이미 있는 테이블 구조를 변경해주지는 않습니다. (예: 컬럼 추가/삭제, 데이터 타입 변경 등은 수동으로 해야 함)
        # 운영 환경에서는 Alembic 같은 마이그레이션 도구를 사용하는 것을 권장합니다.
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db_connections() -> None:
    """앱 종료 시 DB 연결 풀을 정리합니다."""
    await engine.dispose()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """라우터에서 DB 세션을 주입받기 위한 의존성 함수"""
    async with async_session_factory() as session:
        yield session
