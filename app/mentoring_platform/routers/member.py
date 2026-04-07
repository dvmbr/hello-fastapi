from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.mentoring_platform.models.member import Member
from app.mentoring_platform.schemas.common import ListResponse
from app.mentoring_platform.schemas.member import (
    MemberCreate,
    MemberRead,
    MemberUpdate,
)
from app.mentoring_platform.services.member import MemberService


router = APIRouter(prefix="/members", tags=["members"])


def get_member_service(
    session: AsyncSession = Depends(get_db_session),
) -> MemberService:
    return MemberService(session)


@router.post("/", response_model=MemberRead, status_code=201)
async def create_member(
    payload: MemberCreate,
    session: AsyncSession = Depends(get_db_session),
    service: MemberService = Depends(get_member_service),
):
    existing = await service.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    async with session.begin():
        new_member = await service.create(payload)

    return new_member


@router.get("/{member_id}", response_model=MemberRead)
async def read_member(
    member_id: int,
    session: AsyncSession = Depends(get_db_session),
    service: MemberService = Depends(get_member_service),
):
    async with session.begin():
        member = await service.get_by_id(member_id)

        if not member:
            raise HTTPException(status_code=404, detail="멤버를 찾을 수 없습니다.")

    return member


@router.patch("/{member_id}", response_model=MemberRead)
async def update_member(
    member_id: int,
    payload: MemberUpdate,
    session: AsyncSession = Depends(get_db_session),
    service: MemberService = Depends(get_member_service),
):
    async with session.begin():
        member = await service.get_by_id(payload.id)

        if not member:
            raise HTTPException(status_code=404, detail="멤버를 찾을 수 없습니다.")

        member = await service.update(member, payload)
    return member


@router.delete("/{member_id}", status_code=204)
async def delete_member(
    member_id: int,
    session: AsyncSession = Depends(get_db_session),
    service: MemberService = Depends(get_member_service),
):
    async with session.begin():
        member = await service.get_by_id(member_id)

        if not member:
            raise HTTPException(status_code=404, detail="멤버를 찾을 수 없습니다.")

        await service.delete(member)

    return None


@router.get("/", response_model=ListResponse[MemberRead])
async def list_members(
    name: str | None = Query(default=None),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=1),
    session: AsyncSession = Depends(get_db_session),
    service: MemberService = Depends(get_member_service),
):

    async with session.begin():
        members = await service.list(name=name, offset=offset, limit=limit)
        total = len(members)

    return ListResponse[MemberRead](total=total, items=members)
