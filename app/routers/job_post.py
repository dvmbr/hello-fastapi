from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.database import get_db_session
from app.models.company import Company
from app.models.job_post import (
    JobPost,
    JobPostCreate,
    JobPostResponse,
    JobPostWithCompany,
)

router = APIRouter(prefix="/job_posts", tags=["job_posts"])


@router.get(
    "/",
    response_model=list[JobPostWithCompany],
    summary="채용 공고 목록 조회",
    description="채용 공고 목록을 조회하는 엔드포인트입니다.",
    responses={
        200: {"description": "채용 공고 목록 조회 성공"},
        422: {"description": "입력 데이터 유효성 검사 실패"},
    },
)
async def list_job_posts(
    company_name: str | None = Query(
        default=None,
        description="회사 이름으로 채용 공고를 부분 검색합니다 (대소문자 구분 없음)",
    ),
    session: AsyncSession = Depends(get_db_session),
):
    """
    채용 공고 목록을 조회합니다.

    - 반환되는 정보에는 `id`, `title`, `description`, `company_id`, `created_at`이 포함됩니다.
    - 각 채용 공고와 관련된 회사 정보도 함께 반환됩니다.
    """
    statement = select(JobPost).options(selectinload(JobPost.company))
    if company_name:
        statement = statement.join(Company).where(
            Company.name.ilike(f"%{company_name}%")
        )

    result = await session.execute(statement)
    job_posts = result.scalars().all()

    return job_posts


@router.get(
    "/{job_post_id}",
    response_model=JobPostWithCompany,
    summary="채용 공고 정보 조회",
    description="채용 공고 정보를 조회하는 엔드포인트입니다.",
    responses={
        200: {"description": "채용 공고 정보 조회 성공"},
        404: {"description": "채용 공고를 찾을 수 없습니다."},
        422: {"description": "입력 데이터 유효성 검사 실패"},
    },
)
async def get_job_post(
    job_post_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """
    채용 공고 정보를 조회합니다.

    - `job_post_id`: 조회할 채용 공고의 내부 ID입니다.
    - 반환되는 정보에는 `id`, `public_id`, `title`, `description`, `company_id`, `created_at`이 포함됩니다.
    """
    statement = (
        select(JobPost)
        .where(JobPost.id == job_post_id)
        .options(selectinload(JobPost.company))  # JobPost와 관련된 Company도 함께 로드
    )
    result = await session.execute(statement)
    job_post = result.scalar_one_or_none()

    if job_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{job_post_id} is not found"
        )

    return job_post


@router.post(
    "/",
    response_model=JobPostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="채용 공고 생성",
    description="채용 공고를 생성하는 엔드포인트입니다.",
    responses={
        201: {"description": "채용 공고 생성 성공"},
        404: {"description": "회사를 찾을 수 없습니다."},
        422: {"description": "입력 데이터 유효성 검사 실패"},
    },
)
async def create_job_post(
    payload: JobPostCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """
    새로운 채용 공고를 생성합니다.

    - `title`: 채용 공고의 제목입니다.
    - `description`: 채용 공고의 상세 설명입니다 (선택 사항).
    - `company_id`: 채용 공고가 속한 회사의 내부 ID입니다.
    - 반환되는 정보에는 생성된 채용 공고의 `id`, `public_id`, `title`, `description`, `company_id`, `created_at`이 포함됩니다.
    """
    company = await session.get(Company, payload.company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"company {payload.company_id} is not found",
        )

    async with session.begin():
        job_post = JobPost(**payload.model_dump())
        session.add(job_post)
        await session.flush()
        await session.refresh(job_post)

    return job_post


@router.delete(
    "/{job_post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="채용 공고 삭제",
    description="채용 공고를 삭제하는 엔드포인트입니다. 생성 응답의 job_post id를 사용하세요.",
    responses={
        204: {"description": "채용 공고 삭제 성공"},
        404: {"description": "채용 공고를 찾을 수 없습니다."},
        422: {"description": "입력 데이터 유효성 검사 실패"},
    },
)
async def delete_job_post(
    job_post_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """
    채용 공고를 삭제합니다.

    - `job_post_id`: 삭제할 채용 공고의 내부 ID입니다. 보통 생성 응답의 `id`를 사용합니다.
    - 성공적으로 삭제되면 204 No Content 응답이 반환됩니다. `job_post_id`가 존재하지 않을 경우 404 Not Found 에러가 발생합니다.
    """
    async with session.begin():
        job_post = await session.get(JobPost, job_post_id)

        if job_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{job_post_id} is not found",
            )

        await session.delete(job_post)
    return None
