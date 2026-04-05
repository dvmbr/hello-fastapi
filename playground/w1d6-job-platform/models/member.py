from datetime import datetime, timezone
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class MemberRole(str, Enum):
    JOB_SEEKER = "job_seeker"
    RECRUITER = "recruiter"
    ADMIN = "admin"


class Member(SQLModel, table=True):
    __tablename__ = "members"

    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    name: str = Field(min_length=1, max_length=50)
    role: MemberRole = Field(default=MemberRole.JOB_SEEKER)
    age: int = Field(ge=18)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
