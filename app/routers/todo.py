from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.todo import TodoCreate, TodoResponse, TodoUpdate
from app.storage.todo import auto_increment_todo_id, get_todo_db

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get(
    "/",
    response_model=list[TodoResponse],
    summary="할 일 목록 조회",
    responses={
        200: {"description": "할 일 목록 조회 성공"},
        422: {"description": "입력 데이터 유효성 검사 실패"},
    },
)
async def list_todos(
    completed: bool | None = None,
    # 음수 입력 방지
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: dict = Depends(get_todo_db),
):
    """
    할 일 목록을 조회합니다.

    - `completed`: 완료 여부 필터 (선택 사항, true 또는 false)
    - `skip`: 건너뛸 할 일 수 (기본값: 0)
    - `limit`: 조회할 할 일 수 (기본값: 10)
    - 반환되는 정보에는 `id`, `title`, `description`, `completed`가 포함됩니다.
    - `skip`과 `limit`을 사용하여 페이지네이션이 가능합니다. 예를 들어, `skip=0&limit=10`은 첫 번째 페이지, `skip=10&limit=10`은 두 번째 페이지를 의미합니다.
    - `skip`과 `limit`이 음수인 경우 422 Unprocessable Entity 에러가 발생합니다.
    - `limit`이 100보다 큰 경우 422 Unprocessable Entity 에러가 발생합니다.
    - `completed`가 true 또는 false가 아닌 경우 422 Unprocessable Entity 에러가 발생합니다.
    - `completed`가 제공되지 않으면 모든 할 일이 반환됩니다.
    """
    result = list(db.values())

    # /todos?completed=true || /todos?completed=false
    if completed is not None:
        result = [t for t in result if t["completed"] == completed]

    # new_result = []
    #
    # for t in result:
    #   if t["completed"] == completed:
    #       new_result.append(t)
    #
    # result = new_result

    # skip만큼 건너뛰고, limit까지 가져와라
    # /todos?skip=0&limit=10 -> 첫 페이지
    # /todos?skip=10&limit=10 -> 두 번째 페이지
    return result[skip : skip + limit]


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="할 일 조회",
    responses={
        200: {"description": "할 일 조회 성공"},
        404: {"description": "할 일을 찾을 수 없음"},
    },
)
async def get_todo(todo_id: int, db: dict = Depends(get_todo_db)):
    """
    할 일 ID를 기반으로 할 일의 정보를 조회합니다.

    - `todo_id`: 조회할 할 일의 ID (정수)
    - 반환되는 정보에는 `id`, `title`, `description`, `completed`가 포함됩니다.
    - `todo_id`가 존재하지 않을 경우 404 Not Found 에러가 발생합니다.
    """
    if todo_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{todo_id} is not found"
        )

    return db[todo_id]


@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="할 일 생성",
    responses={
        201: {"description": "할 일 생성 성공"},
        422: {"description": "입력 데이터 유효성 검사 실패"},
    },
)
async def create_todo(todo: TodoCreate, db: dict = Depends(get_todo_db)):
    """
    새로운 할 일을 생성합니다.

    - `title`: 할 일의 제목 (필수, 1~100자)
    - `description`: 할 일의 설명 (선택 사항, 최대 500자)
    - `completed`: 할 일의 완료 여부 (기본값: False)
    - 반환되는 정보에는 `id`, `title`, `description`, `completed`가 포함됩니다.
    """
    todo_id = auto_increment_todo_id()

    new_todo = {
        "id": todo_id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
    }

    db[todo_id] = new_todo
    return new_todo


@router.patch(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="할 일 업데이트",
    responses={
        200: {"description": "할 일 업데이트 성공"},
        404: {"description": "할 일을 찾을 수 없음"},
    },
)
async def update_todo(todo_id: int, todo: TodoUpdate, db: dict = Depends(get_todo_db)):
    """
    할 일 ID를 기반으로 할 일을 업데이트합니다.

    - `todo_id`: 업데이트할 할 일의 ID (정수)
    - `title`: 할 일의 제목 (선택 사항, 1~100자)
    - `description`: 할 일의 설명 (선택 사항, 최대 500자)
    - `completed`: 할 일의 완료 여부 (선택 사항)
    - 반환되는 정보에는 `id`, `title`, `description`, `completed`가 포함됩니다.
    - `todo_id`가 존재하지 않을 경우 404 Not Found 에러가 발생합니다.
    """
    if todo_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{todo_id} is not found"
        )

    stored_todo = db[todo_id]

    # 기본 dump             : 모든 필드 포함
    # exclude_unset=True    : 입력된 필드만 포함
    update_data = todo.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        stored_todo[key] = value

    return stored_todo


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="할 일 삭제",
    responses={
        204: {"description": "할 일 삭제 성공"},
        404: {"description": "할 일을 찾을 수 없음"},
    },
)
async def delete_todo(todo_id: int, db: dict = Depends(get_todo_db)):
    """
    할 일 ID를 기반으로 할 일을 삭제합니다.

    - `todo_id`: 삭제할 할 일의 ID (정수)
    - 반환되는 정보에는 `id`, `title`, `description`, `completed`가 포함됩니다.
    - `todo_id`가 존재하지 않을 경우 404 Not Found 에러가 발생합니다.
    """
    if todo_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{todo_id} is not found"
        )

    del db[todo_id]
    return None
