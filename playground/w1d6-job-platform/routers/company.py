from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from models.company import Company, CompanyCreate, CompanyUpdate, CompanyResponse
from pydantic import BaseModel
from database import get_session

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post(
    "/",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회사 생성",
    description="새로운 회사를 생성하는 엔드포인트입니다.",
)
async def create_company(
    payload: CompanyCreate,
    session: AsyncSession = Depends(get_session),
):
    # business_number 중복 체크
    statement = select(Company).where(
        Company.business_number == payload.business_number
    )
    result = await session.execute(statement)
    exists = result.scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Business number already exists.")
    company = Company(**payload.model_dump(exclude_unset=True))
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


# 페이지네이션 응답 모델
class CompanyListResponse(BaseModel):
    total: int
    items: List[CompanyResponse]


@router.get(
    "/",
    response_model=CompanyListResponse,
    summary="회사 목록 조회",
    description="회사 목록을 조회하는 엔드포인트입니다. 페이지네이션을 지원합니다.",
)
async def list_companies(
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수 (최대 100)"),
    offset: int = Query(0, ge=0, description="건너뛸 항목 수 (페이지네이션 시작 위치)"),
    session: AsyncSession = Depends(get_session),
):
    total = await session.scalar(select(func.count()).select_from(Company))
    statement = (
        select(Company).order_by(Company.created_at.desc()).offset(offset).limit(limit)
    )
    result = await session.execute(statement)
    companies = result.scalars().all()
    return CompanyListResponse(total=total, items=companies)


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="회사 단건 조회",
    description="회사 ID로 회사 하나를 조회하는 엔드포인트입니다.",
)
async def get_company(
    company_id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Company).where(Company.id == company_id)
    result = await session.execute(statement)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")
    return company


# 회사 정보 수정 (부분 업데이트)
@router.patch(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="회사 정보 수정",
    description="회사 ID로 회사 정보를 부분 업데이트하는 엔드포인트입니다. 요청 본문에는 업데이트할 필드만 포함하면 됩니다.",
)
async def update_company(
    company_id: int,
    payload: CompanyUpdate,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Company).where(Company.id == company_id)
    result = await session.execute(statement)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(company, key, value)
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


# 회사 삭제
@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="회사 삭제",
    description="회사 ID로 회사를 삭제하는 엔드포인트입니다. 응답 본문은 없습니다.",
)
async def delete_company(
    company_id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Company).where(Company.id == company_id)
    result = await session.execute(statement)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")
    await session.delete(company)
    await session.commit()
    return None
