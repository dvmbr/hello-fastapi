from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class mentor(SQLModel, table=True):
    __tablename__ = "mentors"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=50)
    business_number: str = Field({"unique": True})
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
        ),
    )
