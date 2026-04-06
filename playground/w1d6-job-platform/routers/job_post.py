from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from app.models.job_post import JobPost, JobPostResponse

router = APIRouter(prefix="/job_posts", tags=["job_posts"])


class JobPostListResponse(BaseModel):
    total: int
    items: list[JobPostResponse]


@router.get(
    "/",
    summary="채용 공고 목록 조회",
    description="채용 공고 목록을 조회하는 엔드포인트입니다. 페이지네이션을 지원합니다.",
)
async def list_job_posts():
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수 (최대 100)")
    offset: int = Query(0, ge=0, description="건너뛸 항목 수 (페이지네이션 시작 위치)")

    session: AsyncSession = Depends(get_session)

    total = await session.scalar(select(func.count(JobPost.id)))
    statement = (
        select(JobPost).order_by(JobPost.created_at.desc()).offset(offset).limit(limit)
    )

    result = await session.execute(statement)
    job_posts = result.scalars().all()

    return JobPostListResponse(total=total, items=job_posts)


@router.get(
    "/{job_post_id}",
    summary="채용 공고 정보 조회",
    description="채용 공고 정보를 조회하는 엔드포인트입니다.",
)
async def get_job_post(job_post_id: int):
    return {"message": f"채용 공고 {job_post_id} 정보 조회"}


@router.post(
    "/",
    summary="채용 공고 생성",
    description="새로운 채용 공고를 생성하는 엔드포인트입니다.",
)
async def create_job_post():
    return {"message": "채용 공고 생성"}


@router.put(
    "/{job_post_id}",
    summary="채용 공고 정보 수정",
    description="채용 공고 정보를 수정하는 엔드포인트입니다.",
)
async def update_job_post(job_post_id: int):
    return {"message": f"채용 공고 {job_post_id} 정보 수정"}


@router.delete(
    "/{job_post_id}",
    summary="채용 공고 삭제",
    description="채용 공고를 삭제하는 엔드포인트입니다.",
)
async def delete_job_post(job_post_id: int):
    return {"message": f"채용 공고 {job_post_id} 삭제"}
