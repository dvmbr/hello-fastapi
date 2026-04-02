from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import UserCreate, UserResponse
from app.storage.user import get_user_db, user_id_counter

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="새로운 사용자 생성",
    responses={
        201: {"description": "사용자가 성공적으로 생성되었습니다."},
        400: {"description": "이메일이 이미 존재합니다."},
        422: {"description": "입력 데이터 유효성 검사 실패"},
    },
)
async def create_user(user_data: UserCreate, db: dict = Depends(get_user_db)):
    """
    새로운 사용자를 생성합니다.

    - `email`: 사용자의 이메일 주소 (유효한 이메일 형식이어야 함)
    - `password`: 사용자의 비밀번호 (최소 8자 이상)
    - `name`: 사용자의 이름 (선택 사항, 1~50자)
    - `role`: 사용자 권한 (`user` 또는 `admin`, 기본값 `user`)
    - `profile`: 사용자 프로필 정보 (선택 사항)
        - `phone`: 전화번호 (예: 010-1234-5678)
        - `address`: 주소 정보
            - `city`: 도시 (예: Seoul)
            - `street`: 상세 주소 (예: Teheran-ro 123)
            - `zip_code`: 우편번호 (예: 06134)
    - 반환되는 정보에는 `id`, `email`, `name`, `role`, `profile`, `created_at`이 포함됩니다. 비밀번호는 반환되지 않습니다.
    - 이메일이 이미 존재하는 경우 400 Bad Request 에러가 발생합니다.
    """
    global user_id_counter
    user_id_counter += 1

    new_user = {
        "id": user_id_counter,
        "email": user_data.email,
        "name": user_data.name,
        "role": user_data.role,
        "profile": user_data.profile,
        # 실제로는 해싱 알고리즘 사용
        "hashed_password": f"hashed_{user_data.password}",
        "created_at": datetime.now(),
    }

    db[user_id_counter] = new_user
    return new_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="사용자 정보 조회",
    responses={
        200: {"description": "사용자 정보 조회 성공"},
        404: {"description": "사용자를 찾을 수 없음"},
    },
)
async def get_user(user_id: int, db: dict = Depends(get_user_db)):
    """
    사용자 ID를 기반으로 사용자의 정보를 조회합니다.

    - `user_id`: 조회할 사용자의 ID (정수)
    - 반환되는 정보에는 `id`, `email`, `name`, `role`, `profile`, `created_at`이 포함됩니다. 비밀번호는 반환되지 않습니다.
    - `user_id`가 존재하지 않을 경우 404 Not Found 에러가 발생합니다.
    """
    if user_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{user_id} is not found"
        )

    return db[user_id]


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="사용자 목록 조회",
    responses={
        200: {"description": "사용자 목록 조회 성공"},
        422: {"description": "입력 데이터 유효성 검사 실패"},
    },
)
async def list_users(skip: int = 0, limit: int = 10, db: dict = Depends(get_user_db)):
    """
    사용자 목록을 조회합니다.

    - `skip`: 건너뛸 사용자 수 (기본값: 0)
    - `limit`: 조회할 사용자 수 (기본값: 10)
    - 반환되는 정보에는 `id`, `email`, `name`, `role`, `profile`, `created_at`이 포함됩니다. 비밀번호는 반환되지 않습니다.
    - `skip`과 `limit`을 사용하여 페이지네이션이 가능합니다. 예를 들어, `skip=0&limit=10`은 첫 번째 페이지, `skip=10&limit=10`은 두 번째 페이지를 의미합니다.
    - `skip`과 `limit`이 음수인 경우 422 Unprocessable Entity 에러가 발생합니다.
    """
    users = list(db.values())
    return users[skip : skip + limit]


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="사용자 삭제",
    responses={
        204: {"description": "사용자 삭제 성공"},
        404: {"description": "사용자를 찾을 수 없음"},
    },
)
async def delete_user(user_id: int, db: dict = Depends(get_user_db)):
    """
    사용자 ID를 기반으로 사용자를 삭제합니다.

    - `user_id`: 삭제할 사용자의 ID (정수)
    - `user_id`가 존재하지 않을 경우 404 Not Found 에러가 발생합니다.
    - 성공적으로 삭제된 경우 204 No Content 상태 코드가 반환됩니다.
    """
    if user_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{user_id} is not found"
        )

    del db[user_id]
