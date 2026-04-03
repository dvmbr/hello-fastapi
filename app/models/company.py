import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.job_post import JobPost


class CompanyBase(SQLModel):
    name: str


class Company(CompanyBase, table=True):
    __tablename__ = "companies"

    id: int | None = Field(default=None, primary_key=True)
    public_id: UUID = Field(default_factory=uuid.uuid4, unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # job_posts는 DB에 컬럼으로 생성되지 않고, 코드에서만 쓰이는 속성입니다.
    # Company와 JobPost의 1:N 관계를 ORM에 알려주는 선언
    job_posts: list["JobPost"] = Relationship(back_populates="company")


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int
    public_id: UUID
    created_at: datetime
