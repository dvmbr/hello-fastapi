from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, func


class MentoringPostStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PAUSED = "PAUSED"


class MentoringPost(SQLModel, table=True):
    __tablename__ = "mentoring_posts"
    __table_args__ = (
        CheckConstraint(
            "status IN ('OPEN', 'CLOSED', 'PAUSED')",
            name="ck_mentoring_posts_status_valid",
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
