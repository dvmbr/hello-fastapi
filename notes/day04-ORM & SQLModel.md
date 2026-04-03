# day04 ORM & SQLModel

- SQLModel로 만든 ORM 모델 클래스가 DB에서 정확히 무엇이 되는지
- `table=True`를 붙이면 어떤 일이 생기는지
- 각 필드가 DB 컬럼인지, 코드에서만 쓰는 속성인지
- 왜 어떤 필드는 DB에 저장되고, 어떤 필드는 저장되지 않는지

## ORM 한 줄 정의

ORM(Object-Relational Mapping)은
"관계형 DB 테이블을 객체로 다루기 위한 매핑 규칙"이다.

쉽게 말하면:

- 클래스는 테이블에 대응되고
- 필드는 컬럼에 대응되고
- 객체 1개는 테이블 row 1개에 대응된다

## 컬럼과 속성 구분

자주 하는 실수:
"클래스에 있는 필드는 전부 DB 컬럼이다"라고 생각하는 것.

실제로는 구분해야 한다.

- DB 컬럼으로 저장되는 필드
- 파이썬 객체/응답에서만 쓰는 필드(계산값, 임시값, 응답 전용 값)

그래서 모델을 설계할 때는
"이 값이 DB에 남아야 하나?"를 먼저 판단해야 한다.

## table=True 이해하기

`table=True`는
"이 클래스를 DB 테이블과 매핑되는 모델로 쓰겠다"는 선언이다.

이 선언 이후 내가 확인해야 할 것:

- 어떤 필드가 실제 컬럼이 되는지
- 어떤 제약조건/키/인덱스가 붙는지
- 어떤 필드는 DB에 반영되지 않는지

## 정확도 보완 메모 (중요)

### 1. `table=True`를 붙였다고 DB 테이블이 즉시 생성되지는 않는다

- `table=True`는 매핑 대상으로 등록된다는 의미에 가깝다
- 실제 DB 반영은 `create_all()` 또는 마이그레이션(Alembic)에서 일어난다

### 2. "필드 = 컬럼"은 기본 규칙이지만 예외가 있다

- 관계 필드(Relationship), 클래스 변수(ClassVar), 계산 속성 등은 컬럼이 아닐 수 있다
- 그래서 필드별로 "컬럼/비컬럼"을 의도적으로 구분해야 한다

### 3. "클래스 1개 = 테이블 1개"도 입문용 규칙이다

- 대부분 맞지만, 조인 테이블/상속 매핑 같은 고급 구조에서는 단순 1:1이 아닐 수 있다

## N+1 문제

ORM을 쓸 때 자주 발생하는 대표적인 성능 문제다.

### 원인

데이터 목록을 1번 가져온 뒤, 그 결과 N개에 대해 각각 추가 쿼리를 날리는 패턴.
ORM이 관계 데이터를 "필요할 때마다 자동으로" 쿼리를 날리기 때문에 발생한다.

### 예시

유저 10명을 조회하고, 각 유저의 주문 목록을 가져오는 경우:

```
SELECT * FROM users                              → 1번 (10명 반환)
SELECT * FROM orders WHERE user_id = 1           → 1번
SELECT * FROM orders WHERE user_id = 2           → 1번
...
SELECT * FROM orders WHERE user_id = 10          → 1번

총 11번 쿼리 = 1 + N
```

### 해결 방법

JOIN 또는 eager loading으로 한 번에 가져오도록 바꾼다.

```
SELECT users.*, orders.* FROM users JOIN orders ON ...  → 1번으로 해결
```

SQLAlchemy/SQLModel에서는 `selectinload`, `joinedload` 옵션으로 해결한다.

## 모델 분리 패턴

SQLModel에서 가장 중요한 설계 패턴이다.

### 핵심 아이디어

DB 저장용 모델과 API 요청/응답용 모델을 역할별로 분리한다.

### 왜 분리해야 하는가

DB에는 있어야 하지만 API 응답에 노출하면 안 되는 필드들이 존재한다.

- `hashed_password` → DB에 저장되지만 응답에 절대 노출하면 안 됨
- `created_at` → DB가 관리, 요청 body에는 없어야 함
- `id` → DB가 자동 생성, 요청 body에는 없어야 함

### 3가지 모델 역할

```python
# 1. DB 테이블 모델 (실제 저장)
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str
    hashed_password: str      # DB에만 존재
    created_at: datetime

# 2. 요청 모델 (클라이언트 → 서버)
class UserCreate(SQLModel):   # table=True 없음 → Pydantic 모델
    email: str
    password: str             # 평문 비밀번호, DB에 그대로 저장 안 함

# 3. 응답 모델 (서버 → 클라이언트)
class UserResponse(SQLModel): # table=True 없음
    id: int
    email: str
    created_at: datetime
    # hashed_password 없음 → 응답에서 자동 제외
```

### 현재 프로젝트와 비교

지금 `app/models/user.py`에서도 이미 이 패턴을 쓰고 있다.

- `UserCreate` → 요청 모델
- `UserUpdate` → 부분 수정 요청 모델
- `UserResponse` → 응답 모델 (hashed_password 없음)

SQLModel 도입 후 달라지는 점은 `table=True`가 붙은 `User` 모델이 하나 더 생긴다는 것이다.

### 한 줄 요약

`table=True` 모델(DB용) + Pydantic 모델(요청/응답용)을 역할별로 나누는 게 모델 분리 패턴이다.

## UUID

전 세계에서 중복되지 않도록 설계된 고유 식별자다.

```
550e8400-e29b-41d4-a716-446655440000
```

8-4-4-4-12 자리 16진수, 하이픈으로 구분된 32자리 문자열이다.

### 실무에서 함께 쓰는 이유 (정수 ID + UUID)

요즘 실무에서는 "정수 ID를 버리고 UUID만" 쓰기보다,
역할을 나눠서 같이 쓰는 패턴이 많다.

- `id`(정수): 내부 CRUD, 운영/디버깅, 관리 도구에서 사용
- `public_id`(UUID): 외부 노출용 식별자(API 공유, 링크, 로그 노출)

이렇게 분리하면:

- 내부 작업은 정수 ID로 빠르고 편하게 처리
- 외부에는 UUID를 노출해 추측/열거 위험 완화
- 분산 환경에서 식별자 충돌 위험도 줄일 수 있음

### 파이썬에서 사용

```python
import uuid

str(uuid.uuid4())
# '550e8400-e29b-41d4-a716-446655440000'
```

### SQLModel에서 사용 예 (하이브리드)

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    public_id: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, index=True)
    email: str
```

### 언제 어떤 키를 쓰는가

- 내부 CRUD 경로 파라미터/관리 페이지 → 정수 `id`
- 외부 공개 식별자/노출 가능한 링크 → UUID `public_id`
- 단일 DB 내부에서 빠른 조인/인덱스 중심 작업 → 정수 `id`
- 서비스 간 식별자 공유/분산 생성 요구 → UUID 계열 식별자

## DB 비동기 세션이 필요한 이유

핵심은 서버가 동시에 여러 요청을 받을 때 멈추지 않게 하려는 것이다.

### 왜 필요한가

- DB 작업 대기 시간 동안 다른 요청을 처리할 수 있다.
- 쿼리 응답을 기다리는 동안 이벤트 루프를 막지 않는다.
- FastAPI의 `async` 라우터와 실행 모델에 자연스럽게 맞는다.
- 동시성 트래픽에서 효율이 좋아진다.
- 특히 I/O 대기(쿼리, 네트워크)가 많은 API에서 차이가 커진다.

### 동기 세션 vs 비동기 세션

- 동기 세션: DB 응답을 기다리는 동안 해당 작업 흐름이 블로킹된다.
- 비동기 세션: DB 응답을 기다리는 동안 다른 요청을 먼저 처리할 수 있다.

### 언제 꼭 써야 하나

- 전체 스택을 async로 가져갈 때(`aiosqlite`, `async def` 라우터) 쓰는 게 맞다.
- 작은 학습용/단순 앱은 동기 세션도 충분히 가능하다.
