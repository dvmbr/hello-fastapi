## 서버 실행

```sh
$ DEBUG=true uv run uvicorn app.main:app --reload
```

`http://localhost:8000`에서 서버가 실행됩니다.

## API 문서

- Swagger UI: `http://localhost:8000/docs`
- redoc UI: `http://localhost:8000/redoc`
- JSON 스키마: `http://localhost:8000/openapi.json`

## job_post 생성 테스트 순서

Swagger UI(`http://localhost:8000/docs`)에서 아래 순서로 테스트하면 됩니다.

1. 회사 생성 (`POST /api/v1/companies/`)

```json
{
  "name": "네이버"
}
```

2. 응답의 `id`(정수) 확인

- 이 정수 `id`는 3번 요청의 `company_id`에 **그대로** 사용해야 합니다.
- `public_id`(UUID)는 외부 노출용 식별자이며, CRUD 경로 파라미터로는 `id`를 사용합니다.

```json
{
  "id": 1,
  "public_id": "2f2f8f8b-1111-2222-3333-444444444444",
  "name": "네이버",
  "created_at": "2026-04-04T12:00:00Z"
}
```

3. 채용공고 생성 (`POST /api/v1/job_posts/`)

```json
{
  "title": "Backend Engineer",
  "description": "FastAPI 경험 우대",
  "company_id": 1
}
```

4. 생성 응답의 `id`(정수)로 채용공고 삭제 (`DELETE /api/v1/job_posts/{job_post_id}`)

- 3번 응답의 `id`를 경로 파라미터 `job_post_id`에 그대로 사용합니다.

예시:

```text
DELETE /api/v1/job_posts/1
```
