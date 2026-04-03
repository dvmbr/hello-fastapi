from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_db_session
from app.models.company import Company, CompanyCreate, CompanyResponse

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get(
    "/",
    response_model=list[CompanyResponse],
    summary="회사 목록 조회",
    description="회사 목록을 조회하는 엔드포인트입니다.",
    responses={
        200: {"description": "회사 목록 조회 성공"},
        422: {"description": "입력 데이터 유효성 검사 실패"},
    },
)
async def list_companies(
    name: str | None = Query(
        default=None,
        description="회사 이름으로 부분 검색 (대소문자 구분 없음)",
    ),
    session: AsyncSession = Depends(get_db_session),
):
    """
    회사 목록을 조회합니다.

    - `name`: 회사 이름으로 부분 검색 (선택 사항, 대소문자 구분 없음)
        - `name`이 제공되면 해당 문자열이 포함된 회사만 반환됩니다. 예를 들어, `?name=tech`로 검색하면 "Tech Corp", "Innotech" 등이 반환될 수 있습니다.
    - 반환되는 정보에는 `id`, `name`, `created_at`이 포함됩니다.
    """
    statement = select(Company)
    if name:
        statement = statement.where(Company.name.ilike(f"%{name}%"))

    result = await session.execute(statement)
    companies = result.scalars().all()
    return companies


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="회사 정보 조회",
    description="회사 정보를 조회하는 엔드포인트입니다.",
    responses={
        200: {"description": "회사 정보 조회 성공"},
        404: {"description": "회사를 찾을 수 없습니다."},
        422: {"description": "입력 데이터 유효성 검사 실패"},
    },
)
async def get_company(
    company_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """
    회사 정보를 조회합니다.

    - `company_id`: 조회할 회사의 내부 ID입니다.
    - 반환되는 정보에는 `id`, `public_id`, `name`, `created_at`이 포함됩니다.
    """
    statement = select(Company).where(Company.id == company_id)
    result = await session.execute(statement)
    company = result.scalar_one_or_none()

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{company_id} is not found"
        )
    return company


@router.post(
    "/",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회사 생성",
    description="회사를 생성하는 엔드포인트입니다.",
    responses={
        201: {"description": "회사 생성 성공"},
        422: {"description": "입력 데이터 유효성 검사 실패"},
    },
)
async def create_company(
    payload: CompanyCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """
    새로운 회사를 생성합니다.

    - `name`: 회사 이름입니다.
    - 반환되는 정보에는 `id`, `name`, `created_at`이 포함됩니다.
    """
    company = Company(**payload.model_dump())
    session.add(company)
    await session.flush()
    await session.refresh(company)

    return company
