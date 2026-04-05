from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class ApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    REVIEWING = "REVIEWING"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"


class Application(SQLModel, table=True):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint(
            "member_id",
            "job_post_id",
            name="uq_applications_member_id_job_post_id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    member_id: int = Field(foreign_key="members.id", index=True)
    job_post_id: int = Field(foreign_key="job_posts.id", index=True)
    status: ApplicationStatus = Field(default=ApplicationStatus.APPLIED)
    cover_letter: str | None = Field(default=None, max_length=2000)
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))