# swagger 관리

- `main.py`에서 `openapi_tags` 설정 추가
  - `users`, `todos` 태그 설명을 문서에 표시
- `DEBUG` 환경변수로 문서 노출 제어
  - `docs_url`: DEBUG일 때만 `/docs`
  - `redoc_url`: DEBUG일 때만 `/redoc`
- 라우터 버전 prefix 구조 적용
  - `app.include_router(..., prefix="/api/v1")`
  - 라우터 내부는 도메인 prefix(`/users`, `/todos`)만 관리
- User API 문서 보강
  - `summary`, `responses` 메타데이터 추가
  - 응답 모델 기준으로 민감정보(`hashed_password`) 미노출 유지
- User 모델 확장
  - `role` enum 추가 (`user`, `admin`)
  - `profile.address` 구조 추가
    - `city`, `street`, `zip_code`에 `examples` 반영

- 인증
- `HTTPBearer` 기반 의존성으로 보호 엔드포인트 구성
- 토큰 없음/실패: `401`, 권한 부족: `403`
- Swagger `Authorize` 버튼으로 Bearer 토큰 테스트

- FastAPI 실무 포인트
  - 생성 API는 `201`, 삭제 API는 `204`를 명시하면 문서가 명확해짐
  - 유효성 검증 실패는 기본적으로 `422`가 반환됨
  - 예외는 `HTTPException(status_code=..., detail=...)`로 명시적으로 처리

- OpenAPI 타입 자동 생성 (프론트 연동)
  - 서버 실행 후 `openapi.json`에서 타입 파일 생성
  - 명령어:

```bash
npx openapi-typescript http://localhost:8000/openapi.json -o ./src/api/types.ts
```

## 상태코드 정리 (200~500)

- 2xx (성공)
  - `200 OK`: 요청 성공 (조회/수정 응답 기본)
  - `201 Created`: 리소스 생성 성공 (`POST` 생성)
  - `204 No Content`: 성공했지만 응답 본문 없음 (`DELETE` 자주 사용)

- 3xx (리다이렉션)
  - `301 Moved Permanently`: 영구 이동
  - `302 Found`: 임시 이동
  - `304 Not Modified`: 캐시된 리소스 사용 가능

- 4xx (클라이언트 요청 오류)
  - `400 Bad Request`: 잘못된 요청 형식/파라미터
  - `401 Unauthorized`: 인증 필요 또는 인증 실패
  - `403 Forbidden`: 인증은 되었지만 권한 없음
  - `404 Not Found`: 리소스를 찾을 수 없음
  - `409 Conflict`: 리소스 충돌 (중복 생성 등)
  - `422 Unprocessable Entity`: 요청 형식은 맞지만 검증 실패 (FastAPI/Pydantic에서 자주 발생)

- 5xx (서버 오류)
  - `500 Internal Server Error`: 서버 내부 처리 오류
  - `502 Bad Gateway`: 게이트웨이/프록시가 상위 서버에서 잘못된 응답 수신
  - `503 Service Unavailable`: 서버 과부하/점검 중
  - `504 Gateway Timeout`: 게이트웨이/프록시 타임아웃
