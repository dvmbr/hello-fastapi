from datetime import datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, Column, DateTime, func
from sqlmodel import Field, SQLModel


class MemberRole(StrEnum):
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"
    ADMIN = "ADMIN"


class Member(SQLModel, table=True):
    __tablename__ = "members"
    __table_args__ = (
        CheckConstraint("age >= 18", name="ck_members_age_admitted"),
        CheckConstraint(
            "role IN ('BASIC', 'PREMIUM', 'ADMIN')", name="ck_members_role_valid"
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str = Field(min_length=1, max_length=50)
    role: MemberRole = Field(default=MemberRole.BASIC)
    age: int = Field(ge=18)
    password: str = Field(min_length=8, max_length=128, description="hashed password")
    is_active: bool = Field(default=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
        ),
    )
