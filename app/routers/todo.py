from fastapi import APIRouter, HTTPException, Response, status, Query

from app.models.todo import TodoCreate, TodoUpdate, TodoResponse
from app.storage.todo import todos, todo_id_counter

router = APIRouter()


@router.get("/todos", response_model=list[TodoResponse])
async def list_todos(
    completed: bool | None = None,
    # 음수 입력 방지
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    result = list(todos.values())

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


@router.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{todo_id} is not found"
        )

    return todos[todo_id]


@router.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    global todo_id_counter
    todo_id_counter += 1

    new_todo = {
        "id": todo_id_counter,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
    }

    todos[todo_id_counter] = new_todo
    return new_todo


@router.patch("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo: TodoUpdate):
    if todo_id not in todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{todo_id} is not found"
        )

    stored_todo = todos[todo_id]

    # 기본 dump             : 모든 필드 포함
    # exclude_unset=True    : 입력된 필드만 포함
    update_data = todo.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        stored_todo[key] = value

    return stored_todo


@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{todo_id} is not found"
        )

    del todos[todo_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
