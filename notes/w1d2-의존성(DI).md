# 의존성(DI)

- `Depends`를 쓰는 이유
  - 라우터에서 객체 생성/자원 관리 분리 (관심사 분리)
  - 공통 로직 재사용 쉬움 (DB 세션, 인증 등)
  - 테스트 시 `dependency_overrides`로 가짜 의존성 주입 가능

- `yield` 의존성 패턴
  - `yield` 이전: 자원 준비 (세션 열기)
  - `yield` 이후: 요청 종료 후 정리 코드 실행
  - 실무 패턴: 성공 `commit`, 실패 `rollback`, 마지막 `close`
  - `async with`를 쓰면 세션 close는 컨텍스트 매니저가 보장

- 응답 보안 (`response_model`)
  - 화이트리스트 방식으로 응답 필드 제한
  - `hashed_password` 같은 내부 필드 노출 방지
  - 입력/출력 모델 분리 (`Create`, `Update`, `Response`) 권장

- Pydantic v2 `from_attributes`
  - `model_config = {"from_attributes": True}`
  - ORM 객체 속성(`obj.id`)에서 바로 모델 변환 가능
  - 없으면 `model_validate(vars(obj))` 또는 `Model(**vars(obj))`처럼 dict 변환 필요

- Python 핵심 문법
  - `__init__`: 인스턴스 초기화 메서드 (생성 직후 자동 호출)
  - `*`: 리스트/튜플 언패킹
  - `**`: dict 언패킹 (`Model(**data)`)
  - `vars(obj)`: 일반 객체 속성을 dict 형태로 확인

- FastAPI status code 정리
  - 기본 응답 코드는 보통 `200`
  - `POST` 생성은 `201`을 명시하는 게 표준
  - `DELETE`는 `204 No Content` 권장
  - `204`면 보통 본문 없이 return 생략 가능

- 라우터/스토리지 구조 팁
  - `todo`, `user` 라우터는 분리 유지가 좋음
  - in-memory 저장소도 도메인별 파일 분리 추천 (`storage/todo.py`, `storage/user.py`)
  - 단일 파일 합치기는 초반엔 편해도 확장 시 충돌/복잡도 증가

- 실무에서 꼭 체크
  - import 방식 주의: `from datetime import datetime` vs `import datetime`
  - 타입 힌트에 모듈이 아닌 타입 클래스가 들어가야 함

- 한 줄 요약
  - FastAPI 실무 핵심은 "의존성 분리 + 세션 생명주기 관리 + 응답 스키마 통제".
