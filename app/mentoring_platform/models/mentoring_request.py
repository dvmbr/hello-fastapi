from datetime import datetime
from enum import StrEnum

from pydantic import Field
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    func,
)
from sqlmodel import SQLModel


class MentoringRequestStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class MentoringRequest(SQLModel(), table=True):
    __tablename__ = "mentoring_requests"
    __table_args__ = (
        # status 값의 유효성 보장 (PENDING, ACCEPTED, REJECTED만 허용)
        CheckConstraint(
            "status IN ('PENDING', 'ACCEPTED', 'REJECTED')",
            name="ck_mentoring_requests_status_valid",
        ),
        # mentoring_post_id + status 복합 인덱스: 특정 멘토링 글의 요청을 상태별로 빠르게 조회
        # 예) WHERE mentoring_post_id=... AND status=...
        Index("ix_mentoring_requests_post_status", "mentoring_post_id", "status"),
        # member_id 인덱스: 특정 멤버가 보낸 모든 요청을 빠르게 조회
        # 예) WHERE member_id=...
        Index("ix_mentoring_requests_member_id", "member_id"),
        # status + requested_at 인덱스: 상태별로 최근 요청을 빠르게 정렬/조회
        # 예) WHERE status=... ORDER BY requested_at DESC
        Index("ix_mentoring_requests_status_requested_at", "status", "requested_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    member_id: int | None = Field(
        default=None,
        sa_column=Column(
            Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True
        ),
    )
    mentoring_post_id: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("mentoring_posts.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    status: MentoringRequestStatus = Field(default=MentoringRequestStatus.PENDING)
    message: str | None = None
    requested_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
        ),
    )
