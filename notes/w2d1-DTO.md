# DTO

- DTO(Data Transfer Object)는 계층 간 데이터 전달을 위한 객체로, 데이터 검증과 변환을 담당한다.
- Model 하나로 CRUD를 모두 처리하는 대신, Create/Update 등 용도별로 DTO를 분리하여 명확한 역할과 검증 로직을 구현한다.

## Pydantic Validator/Mixin 실무 정리

- 공통 필드와 검증 로직(validator, model_validator)은 Mixin(예: MemberValidatorMixin)에 정의해두고, 각 DTO에서 상속해 재사용한다.
- 필수/옵셔널 여부는 각 DTO에서 override한다.
- 예시)
  - 이메일: 대문자 포함 불가 (field_validator)
  - 비밀번호: 공백 불가, 길이 제한 (field_validator + Field)
  - 이름: 한글/영문/숫자/공백만 허용 (field_validator)
  - 역할/나이: 역할별 최소 나이 제한 (model_validator)

```python
class MemberValidatorMixin(BaseModel):
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    name: str | None = Field(default=None, min_length=1, max_length=50)
    role: MemberRole | None = Field(default=None)
    age: int | None = Field(default=None, ge=18)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is None:
            return v
        if any(c.isupper() for c in v):
            raise ValueError("이메일은 소문자만 허용됩니다.")
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        if ' ' in v:
            raise ValueError("비밀번호에 공백이 포함될 수 없습니다.")
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is None:
            return v
        import re
        if not re.match(r'^[가-힣a-zA-Z0-9 ]+$', v):
            raise ValueError("이름은 한글, 영문, 숫자, 공백만 허용됩니다.")
        return v

    @model_validator(mode="after")
    def validate_age_role(self):
        if self.role == MemberRole.ADMIN and (self.age is None or self.age < 21):
            raise ValueError("관리자는 최소 21세 이상이어야 합니다.")
        if self.role == MemberRole.MENTOR and (self.age is None or self.age < 20):
            raise ValueError("멘토는 최소 20세 이상이어야 합니다.")
        return self
```

- MemberCreate/MemberUpdate 등에서 상속만 하면 모든 검증이 자동 적용됨.

## 검증 레이어 구분

- 프론트와 백엔드 모두에서 검증이 필요하지만, 역할이 다르므로 레이어를 구분하는 것이 좋다.

### 프론트

- 사용자 경험 개선, 즉각적인 피드백 제공이 목적.
- 이메일 중복, 비밀번호 강도, 실시간 입력 검증 등 UI/UX 개선에 집중.

### 백엔드

- 데이터 무결성 보장, 보안 강화가 목적.
- 이메일 형식, 비밀번호 정책, 필드간 상호 검증 등 서버 측에서 최종적으로 데이터 검증.

### 결론

- DTO는 백엔드에서 데이터 검증과 변환을 담당하며, 프론트엔드에서는 별도의 검증 로직이나 라이브러리를 사용하여 사용자 입력을 검증하는 것이 일반적이다.

---

## Pydantic model_dump() 옵션 정리

- **exclude_unset=True**: 실제로 값이 할당(입력)된 필드만 dict에 포함. 기본값만 있는 필드는 제외됨. (주로 PATCH 등 부분 업데이트에 사용)
- **exclude_none=True**: 값이 None인 필드는 dict에서 제외됨. (명시적으로 None이 들어온 값도 결과에서 빠짐)
- 둘 다 True로 주면 "입력된 값 중 None이 아닌 것만" dict에 남음.
- unset: 입력 자체가 없으므로 기존값 유지
- none: 입력을 none으로 명시적으로 했으므로 기존값을 None으로 업데이트

예시:

```python
class User(BaseModel):
    name: str = "default"
    age: int | None = None

u = User()
u.model_dump(exclude_unset=True)   # {}  (입력값 없음)
u.model_dump(exclude_none=True)    # {'name': 'default'}  (None 필드 제외)
User(name="a", age=None).model_dump(exclude_unset=True)  # {'name': 'a', 'age': None}
User(name="a", age=None).model_dump(exclude_none=True)   # {'name': 'a'}
```

## Model -> DTO 변환 흐름

1. 클라이언트 요청 -> JSON 수신
2. Pydantic DTO로 파싱 및 검증 (예: MemberCreate같은 DTO) -> 검증 + 변환된 DTO 객체 생성 **실패시 422 에러**
3. DTO -> ORM 모델 변환 (예: Member같은 SQLModel) -> DB 저장 **실패시 500 에러**
4. DB에서 ORM 모델 조회 -> DTO로 변환 (예: MemberRead 같은 response_model)
5. DTO -> JSON 응답 반환
6. 클라이언트에서 JSON 수신

- DTO는 계층 간 데이터 전달과 검증을 담당하며, Model은 DB와의 상호작용을 담당하는 역할 분리가 중요하다.
- DTO에서 검증이 실패하면 클라이언트에게 422 Unprocessable Entity 에러가 반환되고, DB 저장 과정에서 문제가 발생하면 500 Internal Server Error가 반환된다.
- DTO를 활용하면 각 계층의 책임이 명확해지고, 유지보수성과 확장성이 향상된다.
