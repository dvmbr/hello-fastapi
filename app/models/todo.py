from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100,
        description="할 일의 제목입니다. 최소 1자, 최대 100자까지 입력 가능합니다.",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="할 일의 설명입니다. 최대 500자까지 입력 가능합니다.",
    )
    completed: bool = Field(
        default=False, description="할 일의 완료 여부입니다. 기본값은 False입니다."
    )


class TodoUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="할 일의 제목입니다. 최소 1자, 최대 100자까지 입력 가능합니다.",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="할 일의 설명입니다. 최대 500자까지 입력 가능합니다.",
    )
    completed: bool | None = Field(default=None, description="할 일의 완료 여부입니다.")


class TodoResponse(BaseModel):
    id: int = Field(..., description="할 일의 ID입니다.")
    title: str = Field(..., description="할 일의 제목입니다.")
    description: str | None = Field(None, description="할 일의 설명입니다.")
    completed: bool = Field(..., description="할 일의 완료 여부입니다.")
