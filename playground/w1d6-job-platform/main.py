from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import create_tables, close_db_connections
from routers import company


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 처리할 작업"""
    # startup: DB 스키마 생성
    await create_tables()
    yield
    # shutdown: DB 연결 풀 정리
    await close_db_connections()


app = FastAPI(
    title="w1d6-job-platform",
    lifespan=lifespan,
    description="""
    w1d6-job-platform은 FastAPI 프레임워크를 사용하여 만든 간단한 채용 공고 플랫폼 API 서버입니다.

    response schema는 다음과 같습니다.

    Companies:
        - CompanyResponse: {
            id: str, 
            name: str, 
            business_number: str, 
            created_at: datetime(UTC)
        }
        - CompanyListResponse: {
            total: int,
            items: list[CompanyResponse]
        }
    """,
)

app.include_router(company.router)
