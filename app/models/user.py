from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str | None = Field(default=None, min_length=1, max_length=50)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = Field(default=None, min_length=1, max_length=50)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str | None = None
    created_at: datetime

    # ORM 객체(속성 기반)를 Pydantic 모델로 직접 변환 허용
    # SQLAlchemy 등 ORM 인스턴스를 response_model로 쓸 때 필요
    #
    # 예시:
    #   orm_user = db.get(User, 1)       # SQLAlchemy 객체 (dict 아님)
    #   UserResponse.model_validate(orm_user)   # from_attributes=True 덕분에 동작
    #
    #   없으면: UserResponse.model_validate({"id": 1, "email": ...}) 또는 UserResponse(**vars(orm_user)) 처럼 dict로 직접 변환해야 함
    model_config = {"from_attributes": True}
