# 기록

일일마다 기억해야 할것들 기록

## day 01

- FastAPI = 서버 아님

- Uvicorn = 서버

- ASGI = FastAPI & Uvicorn 연결 규칙

- Swagger 자동 생성됨

- 동기 비동기 함수
  - `async def`: **I/O 바운드 작업**<br>
    (DB 조회, 외부 API 호출, 파일 읽기/쓰기 등)

  - `def`: **CPU 바운드 작업**<br>
    (복잡한 계산, 이미지 처리 등)

- Parameter
  - `Path Parameter`: **이게 누구인가**, 특정 리소스 식별에 사용<br>
    `GET /users/123`

  - `Query Parameter`: **어떤 조건인가**, 필터링이나 페이지네이션 같은 부가 조건에 사용<br>
    `GET /posts?page=2&size=20`

- Field()
  - 타입 외 추가 제약조건<br>
    `password: str = Field(min_length=8, max_length=100)`

- fastapi[standard]
  - Uvicorn, Pydantic, 이메일, 폼 처리 관련 패키지 등
  - standard 말고 all 도 있음
