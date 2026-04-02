## 서버 실행

```sh
$ uv run uvicorn app.main:app --reload
```

`http://localhost:8000`에서 서버가 실행됩니다.

## API 문서

- Swagger UI: `http://localhost:8000/docs`
- redoc UI: `http://localhost:8000/redoc`
- JSON 스키마: `http://localhost:8000/openapi.json`
