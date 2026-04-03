import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.company import Company, CompanyResponse


class JobPostBase(SQLModel):
    title: str
    description: str | None = None


class JobPost(JobPostBase, table=True):
    __tablename__ = "job_posts"

    id: int | None = Field(default=None, primary_key=True)
    public_id: UUID = Field(default_factory=uuid.uuid4, unique=True, index=True)
    company_id: int = Field(foreign_key="companies.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    company: Company | None = Relationship(back_populates="job_posts")


class JobPostCreate(JobPostBase):
    company_id: int


class JobPostResponse(JobPostBase):
    id: int
    public_id: UUID
    company_id: int
    created_at: datetime


class JobPostWithCompany(JobPostResponse):
    company: CompanyResponse | None
