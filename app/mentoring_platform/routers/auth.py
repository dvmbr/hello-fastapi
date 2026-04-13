from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.mentoring_platform.schemas.common import ListResponse
from app.mentoring_platform.schemas.auth import (
    MemberLogin,
    MemberRegister,
    MemberRead,
    MemberUpdate,
    Token,
)
from app.mentoring_platform.services.auth import AuthService


router = APIRouter(prefix="/members", tags=["members"])


# Dependency Injection을 위한 서비스 제공자 함수를 정의합니다.
def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
) -> AuthService:
    return AuthService(session)


@router.post("/register", response_model=MemberRead, status_code=201)
async def register(
    payload: MemberRegister,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    existing = await auth_service.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    async with session.begin():
        new_member = await auth_service.create_member(payload)

    return new_member


@router.post("/login", response_model=Token)
async def login(
    payload: MemberLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    member = await auth_service.authenticate(payload.email, payload.password)
    if not member:
        raise HTTPException(
            status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )

    if not member.is_active:
        raise HTTPException(
            status_code=403, detail="비활성화된 계정입니다. 관리자에게 문의하세요."
        )
