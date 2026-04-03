from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class Address(BaseModel):
    city: str = Field(
        ...,
        description="도시",
        examples=["Seoul"],
    )
    street: str = Field(
        ...,
        description="상세 주소",
        examples=["Teheran-ro 123"],
    )
    zip_code: str = Field(
        ...,
        description="우편번호",
        examples=["06134"],
    )


class Profile(BaseModel):
    phone: str = Field(
        ...,
        description="전화번호",
        examples=["010-1234-5678"],
    )
    address: Address = Field(
        ...,
        description="주소 정보",
    )


class UserCreate(BaseModel):
    email: EmailStr = Field(
        ..., description="사용자의 이메일입니다. 유효한 이메일 형식이어야 합니다."
    )
    password: str = Field(
        min_length=8, description="사용자의 비밀번호입니다. 최소 8자 이상이어야 합니다."
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="사용자의 이름입니다. 최소 1자, 최대 50자까지 입력 가능합니다.",
    )
    role: UserRole = Field(
        default=UserRole.USER,
        description="사용자 권한입니다. user 또는 admin 값을 가집니다.",
    )
    profile: Profile | None = Field(
        default=None,
        description="사용자 프로필 정보입니다.",
    )


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(default=None, description="사용자의 이메일입니다.")
    name: str | None = Field(
        default=None, min_length=1, max_length=50, description="사용자의 이름입니다."
    )
    role: UserRole | None = Field(
        default=None,
        description="사용자 권한입니다. user 또는 admin 값을 가집니다.",
    )
    profile: Profile | None = Field(
        default=None,
        description="사용자 프로필 정보입니다.",
    )


class UserResponse(BaseModel):
    id: int = Field(..., description="사용자의 ID입니다.")
    email: EmailStr = Field(..., description="사용자의 이메일입니다.")
    name: str | None = Field(None, description="사용자의 이름입니다.")
    role: UserRole = Field(..., description="사용자 권한입니다.")
    profile: Profile | None = Field(None, description="사용자 프로필 정보입니다.")
    created_at: datetime = Field(..., description="사용자 생성 일시입니다.")

    # model_config = {"from_attributes": True}
    # ORM 객체(속성 기반)를 Pydantic 모델로 직접 변환 허용
    # SQLAlchemy 등 ORM 인스턴스를 response_model로 쓸 때 필요
    #
    # 예시:
    #   orm_user = db.get(User, 1)       # SQLAlchemy 객체 (dict 아님)
    #   UserResponse.model_validate(orm_user)   # from_attributes=True 덕분에 동작
    #
    #   없으면: UserResponse.model_validate({"id": 1, "email": ...}) 또는 UserResponse(**vars(orm_user)) 처럼 dict로 직접 변환해야 함
    model_config = {"from_attributes": True}
