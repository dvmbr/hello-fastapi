# Day05 DB 비동기 세션 정리

## 1) 지금은 요청마다 세션을 만들고 있나?

결론: 예.

현재 구조에서는 요청마다 `AsyncSession`이 새로 생성되고, 요청이 끝나면 정리된다.

흐름:

1. 요청이 라우터로 들어온다.
2. `Depends(get_db_session)`가 실행된다.
3. `async_sessionmaker`로 `AsyncSession`을 생성한다.
4. 라우터에서 같은 세션으로 DB 작업을 수행한다.
5. 요청 종료 시 세션이 닫힌다.

중요:

- `engine`은 요청마다 새로 만들지 않는다. 앱 전역에서 재사용한다.
- 요청 단위로 바뀌는 것은 `session`이다.

## 2) Async SQLAlchemy 구조는 무엇인가?

한 줄 구조:

- `Engine(앱 전역)` + `SessionFactory(앱 전역)` + `Session(요청 단위)` + `Transaction(작업 단위)`

### Engine

- DB 연결 풀과 드라이버를 관리하는 전역 객체
- 앱 시작 시 생성, 요청마다 재사용

### SessionFactory (`async_sessionmaker`)

- `AsyncSession`을 생성하는 팩토리
- 전역으로 1회 생성 후 재사용

### Session (`AsyncSession`)

- ORM 작업 단위 (조회/추가/수정/삭제)
- 보통 요청 단위로 생성/종료

### Transaction

- commit/rollback 경계를 의미
- 방식 A: 의존성에서 자동 commit/rollback
- 방식 B: `async with session.begin():`로 명시 관리 (실무에서 선호)

### Driver

- DB 종류와 async 드라이버를 맞춰야 함
- SQLite: `sqlite+aiosqlite`
- PostgreSQL: `postgresql+asyncpg`

## 3) 요청 1건 처리 시 실행 순서

1. FastAPI가 의존성으로 세션을 준비한다.
2. 라우터가 `await session.execute(...)` 같은 비동기 쿼리를 수행한다.
3. 트랜잭션 정책에 따라 commit/rollback 한다.
4. 세션을 정리(close)한다.

## 4) 현재 프로젝트에서 기억할 점

- async 스택은 이미 맞춰져 있다 (`create_async_engine`, `AsyncSession`, `aiosqlite`).
- 세션은 요청 단위로 생성된다.
- 트랜잭션 경계를 더 명확히 하려면 `session.begin()` 패턴으로 점진 전환하면 된다.

## 5) "비동기 서버에서 DB 연결이 위험하다"는 말의 의미

핵심: DB 자체가 위험하다는 뜻이 아니라, 비동기 서버에서 DB 사용 패턴을 잘못 잡으면 성능/안정성이 무너질 수 있다는 뜻이다.

대표 리스크:

1. 이벤트 루프 블로킹

- async 서버에서 동기 DB 호출을 쓰면, 쿼리 대기 동안 다른 요청도 지연된다.

2. 세션/커넥션 누수

- 세션을 열고 닫지 않으면 연결이 고갈되어 타임아웃이 발생할 수 있다.

3. 트랜잭션 경계 불명확

- commit/rollback 시점이 불명확하면 부분 저장, 의도치 않은 커밋 같은 정합성 문제가 생긴다.

안전한 패턴:

- 엔진은 앱 전역 재사용
- 세션은 요청 단위 생성/정리
- 트랜잭션 경계 명확화 (`session.begin()`)

## 6) Connection Pool 정리

### 커넥션 풀이란?

- DB 연결을 매 요청마다 새로 만들고 버리지 않고, 미리 만들어 둔 연결을 재사용하는 방식이다.
- 목적은 연결 생성/종료 비용을 줄이고, 동시 요청에서도 안정적으로 처리하는 것이다.

### 왜 필요한가?

- 연결 생성은 생각보다 비싸다(TCP, 인증, 초기화).
- 풀을 쓰면 응답 지연이 줄고, DB에 과도한 연결 폭증을 막을 수 있다.
- 최대 연결 수를 제한해 서버가 과부하 상태로 무너지는 것을 완화할 수 있다.

### Async SQLAlchemy에서 풀의 위치

- `create_async_engine(...)`로 만든 `engine`이 풀을 관리한다.
- `AsyncSession`은 필요할 때 엔진 풀에서 연결을 빌려 쓰고, 작업 후 반납한다.

### 지금 프로젝트(SQLite)에서는?

- SQLite는 파일 기반 DB라 PostgreSQL/MySQL처럼 네트워크 커넥션 풀 이득이 크게 보이지 않을 수 있다.
- 그래도 구조 자체는 동일하게 엔진 재사용 패턴을 유지하는 것이 좋다.
- 중요한 점은 요청마다 `engine`를 새로 만들지 않는 것이다.

### 운영 DB(PostgreSQL 등)에서의 핵심 튜닝 포인트

- `pool_size`: 기본 유지 연결 수
- `max_overflow`: 순간 트래픽에서 추가 허용 연결 수
- `pool_timeout`: 풀에서 연결을 기다리는 최대 시간
- `pool_recycle`: 오래된 연결을 재생성하는 주기

### 실무 체크리스트

- 엔진은 앱 시작 시 1회 생성 후 재사용
- 요청마다 세션 생성/종료
- 세션 누수 방지 (`async with` 사용)
- 풀 고갈 시 타임아웃 로그 모니터링

## 7) engine 설정 변경 요약

### 기존

```python
engine = create_async_engine(DATABASE_URL, echo=True)
```

- 기본 풀 설정 사용
- 환경별 튜닝 여지가 적음

### 변경 후

```python
engine = create_async_engine(
	DATABASE_URL,
	echo=True,
	pool_size=DB_POOL_SIZE,
	max_overflow=DB_MAX_OVERFLOW,
	pool_timeout=DB_POOL_TIMEOUT,
	pool_recycle=DB_POOL_RECYCLE,
	pool_pre_ping=True,
)
```

- 환경변수 기반으로 풀 정책을 조절 가능
- 트래픽/운영 환경에 맞춘 튜닝 가능

### 옵션 의미

- `pool_size`: 풀에 기본으로 유지할 연결 수
- `max_overflow`: 순간 트래픽 시 추가로 열 수 있는 임시 연결 수
- `pool_timeout`: 풀에서 연결을 기다리는 최대 시간(초)
- `pool_recycle`: 오래된 연결을 주기적으로 재생성하는 기준 시간(초)
- `pool_pre_ping`: 풀에서 꺼낸 연결이 살아있는지 확인 후 사용

## 8) `async_session_factory` 설정 의미

코드:

```python
async_session_factory = async_sessionmaker(
	bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)
```

옵션 의미:

- `bind=engine`: 이 세션 팩토리가 사용할 DB 엔진을 지정한다.
- `class_=AsyncSession`: 생성할 세션 타입을 비동기 세션으로 고정한다.
- `expire_on_commit=False`: commit 후에도 ORM 객체 속성을 바로 읽을 수 있게 한다.
- `autoflush=False`: 쿼리 직전에 자동 flush를 하지 않게 하여 flush 시점을 명시적으로 제어한다.

실무 포인트:

- `expire_on_commit=False`는 API 응답 직전에 객체 속성 접근이 끊기는 문제를 줄여준다.
- `autoflush=False`는 의도치 않은 SQL 실행을 줄여 디버깅과 쿼리 제어에 유리하다.

## 9) 이번 변경 작업 한 줄 요약

이번 작업의 핵심은 "DB 비동기 세션 + 트랜잭션 책임 분리"다.

### 메인 변경

- 세션은 의존성에서 요청 단위로 생성/정리
- 쓰기 로직은 `session.begin()`으로 트랜잭션 경계 명시
- 조회 로직은 read-only 패턴으로 유지

### 함께 반영된 변경

- `config` 모듈로 설정 분리
- `pydantic-settings` 기반 환경변수 로딩 전환
- DB 풀 옵션(`pool_size`, `max_overflow`, `pool_timeout`, `pool_recycle`, `pool_pre_ping`) 설정 가능화
