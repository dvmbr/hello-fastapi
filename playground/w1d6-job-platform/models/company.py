from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


# DB 테이블 모델
class Company(SQLModel, table=True):
    __tablename__ = "companies"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=100)
    business_number: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# 입력/출력 스키마
class CompanyCreate(SQLModel):
    name: str
    business_number: str


class CompanyUpdate(SQLModel):
    name: str | None = None
    business_number: str | None = None


# API 응답 전용 모델
class CompanyResponse(SQLModel):
    id: int
    name: str
    business_number: str
    created_at: datetime
