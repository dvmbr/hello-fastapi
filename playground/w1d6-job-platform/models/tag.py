from sqlmodel import Field, SQLModel


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, min_length=1, max_length=50)