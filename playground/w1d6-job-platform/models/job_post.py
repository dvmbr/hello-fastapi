from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class JobPostStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PAUSED = "PAUSED"


class JobPost(SQLModel, table=True):
    __tablename__ = "job_posts"

    id: int | None = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=2000)
    status: JobPostStatus = Field(default=JobPostStatus.OPEN)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobPostCreate(SQLModel):
    company_id: int
    title: str
    description: str


class JobPostUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    status: JobPostStatus | None = None


class JobPostResponse(SQLModel):
    id: int
    company_id: int
    title: str
    description: str
    status: JobPostStatus
    created_at: datetime
