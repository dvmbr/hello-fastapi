from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from app.mentoring_platform.models.member import MemberRole


class ValidatorMixin(BaseModel):
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    name: str | None = Field(default=None, min_length=1, max_length=50)
    role: MemberRole | None = Field(default=None)
    age: int | None = Field(default=None)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v is None:
            return v
        if any(c.isupper() for c in v):
            raise ValueError("이메일은 소문자만 허용됩니다.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        if " " in v:
            raise ValueError("비밀번호에 공백이 포함될 수 없습니다.")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is None:
            return v
        import re

        if not re.match(r"^[가-힣a-zA-Z0-9 ]+$", v):
            raise ValueError("이름은 한글, 영문, 숫자, 공백만 허용됩니다.")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v is None:
            return v
        if v not in MemberRole:
            raise ValueError("유효하지 않은 역할입니다.")
        return v

    @model_validator(mode="after")
    def validate_age_role(self):

        if self.role == MemberRole.ADMIN and (self.age is None or self.age < 21):
            raise ValueError("관리자는 최소 21세 이상이어야 합니다.")

        return self


class MemberRegister(ValidatorMixin):
    # 회원 가입에 필요한 필드들을 정의합니다.
    email: EmailStr
    password: str
    name: str
    role: MemberRole = Field(default=MemberRole.BASIC)
    age: int = Field(ge=18)


class MemberLogin(BaseModel):
    # 로그인에 필요한 필드들을 정의합니다.
    email: EmailStr
    password: str


class Token(BaseModel):
    # 토큰 정보를 정의합니다.
    access_token: str
    token_type: str = "bearer"


class MemberRead(BaseModel):
    # 회원 정보를 읽기 위한 모델입니다. (비밀번호 제외)
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    role: MemberRole
    age: int

    @computed_field
    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.role.value})"


class MemberUpdate(ValidatorMixin):
    # 회원 정보를 업데이트하기 위한 모델입니다. (업데이트할 필드만 포함)
    pass
