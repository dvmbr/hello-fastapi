from datetime import datetime
from enum import StrEnum

from pydantic import Field
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, func
from sqlmodel import SQLModel


class MentoringRequestStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class MentoringRequest(SQLModel(), table=True):
    __tablename__ = "mentoring_requests"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'ACCEPTED', 'REJECTED')",
            name="ck_mentoring_requests_status_valid",
        ),
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
