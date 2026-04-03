from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import close_db_connections, create_db_and_tables
from app.routers import company, job_post, todo, user


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_db_and_tables()
    yield
    await close_db_connections()


app = FastAPI(
    lifespan=lifespan,
    title="Hello FastAPI",
    # API description은 Swagger UI에서 보이는 내용입니다. Markdown 형식도 지원합니다.
    description="""
    Hello FastAPI는 FastAPI 프레임워크를 사용하여 만든 간단한 API 서버입니다.

    이 서버는 사용자 관리와 할 일 관리 기능을 제공합니다.
    + 회사와 채용 공고 관리 기능도 제공합니다.

    User, Todo는 메모리 기반 저장소를 사용하여 CRUD 기능을 구현하였고,
    Company와 Job Post는 SQLModel과 SQLite를 사용하여 데이터베이스에 저장하는 방식으로 구현하였습니다.

    ## 주요 기능
    - User CRUD (생성, 조회, 업데이트, 삭제)
    - Todo CRUD (생성, 조회, 업데이트, 삭제)
    - Company CR (생성, 조회) — 업데이트, 삭제 미구현
    - Job Post CRD (생성, 조회, 삭제) — 업데이트 미구현
    """,
    version="1.0.0",
    contact={
        "name": "dvmbr",
        "email": "itsdvmbr@gmail.com",
    },
    openapi_tags=[
        {
            "name": "users",
            "description": "사용자 관련 API 엔드포인트",
        },
        {
            "name": "todos",
            "description": "할 일 관련 API 엔드포인트",
        },
        {
            "name": "companies",
            "description": "회사 관련 API 엔드포인트",
        },
        {
            "name": "job_posts",
            "description": "채용 공고 관련 API 엔드포인트",
        },
    ],
    docs_url="/docs" if settings.debug else None,  # DEBUG 모드일 때만 Swagger UI 활성화
    redoc_url="/redoc" if settings.debug else None,  # DEBUG 모드일 때만 ReDoc 활성화
)


@app.get(
    "/",
    summary="루트 엔드포인트",
    description="서버가 정상적으로 실행되고 있는지 확인하는 엔드포인트입니다.",
)
async def root():
    return {"message": "Hello", "docs": "/docs"}


app.include_router(todo.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(company.router, prefix="/api/v1")
app.include_router(job_post.router, prefix="/api/v1")
