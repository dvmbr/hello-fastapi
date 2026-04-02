import os

from fastapi import FastAPI

from app.routers import todo, user

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

app = FastAPI(
    title="Hello FastAPI",
    # API description은 Swagger UI에서 보이는 내용입니다. Markdown 형식도 지원합니다.
    description="""
    Hello FastAPI는 FastAPI 프레임워크를 사용하여 만든 간단한 API 서버입니다.

    이 서버는 사용자 관리와 할 일 관리 기능을 제공합니다.

    ## 주요 기능
    - User CRUD (생성, 조회, 업데이트, 삭제)
    - Todo CRUD (생성, 조회, 업데이트, 삭제)
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
    ],
    docs_url="/docs" if DEBUG else None,  # DEBUG 모드일 때만 Swagger UI 활성화
    redoc_url="/redoc" if DEBUG else None,  # DEBUG 모드일 때만 ReDoc 활성화
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
