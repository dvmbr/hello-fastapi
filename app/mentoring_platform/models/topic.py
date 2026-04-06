from sqlmodel import Field, SQLModel


class Topic(SQLModel, table=True):
    __tablename__ = "topics"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field({"unique": True})
