from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    func,
    text,
)


class MentoringPostStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PAUSED = "PAUSED"


class MentoringPost(SQLModel, table=True):
    __tablename__ = "mentoring_posts"
    __table_args__ = (
        # status 값의 유효성 보장 (OPEN, CLOSED, PAUSED만 허용)
        CheckConstraint(
            "status IN ('OPEN', 'CLOSED', 'PAUSED')",
            name="ck_mentoring_posts_status_valid",
        ),
        # mentor_id + status 복합 인덱스: 특정 멘토의 글 중에서 status가 'OPEN'인 것만 빠르게 조회
        # 예) WHERE mentor_id=... AND status='OPEN'
        Index(
            "ix_mentoring_posts_mentor_status",
            "mentor_id",
            sqlite_where=text("status = 'OPEN'"),
        ),
        # id + status 조건부 인덱스: status가 'OPEN'인 글의 id로 빠르게 조회
        # 예) WHERE id=... AND status='OPEN'
        Index(
            "ix_mentoring_posts_id_status", "id", sqlite_where=text("status = 'OPEN'")
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    mentor_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("mentors.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    title: str
    description: str | None = None
    status: MentoringPostStatus = Field(default=MentoringPostStatus.OPEN)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
        ),
    )
