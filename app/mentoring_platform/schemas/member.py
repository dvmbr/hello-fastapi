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


class MemberValidatorMixin(BaseModel):
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    name: str | None = Field(default=None, min_length=1, max_length=50)
    role: MemberRole | None = Field(default=None)
    age: int | None = Field(default=None, ge=18)

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


class MemberCreate(MemberValidatorMixin):
    email: EmailStr
    password: str
    name: str
    role: MemberRole = Field(default=MemberRole.BASIC)
    age: int = Field(ge=18)


class MemberRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )  # SQLAlchemy 모델의 속성에서 데이터를 읽어올 수 있도록 설정합니다.

    id: int
    email: EmailStr
    name: str
    role: MemberRole
    age: int

    @computed_field
    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.role.value})"


class MemberUpdate(MemberValidatorMixin):
    pass
