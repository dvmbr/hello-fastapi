from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlmodel import Field, SQLModel


class SocialAccount(SQLModel, table=True):
    __tablename__ = "social_accounts"
    __table_args__ = UniqueConstraint(
        "provider", "provider_user_id", name="uq_social_accounts_provider_user"
    )

    id: int | None = Field(default=None, primary_key=True)
    member_id: int = Field(
        sa_column=Column(Integer, ForeignKey("members.id", ondelete="CASCADE")),
        nullable=False,
    )
    provider: str = Field(min_length=1, max_length=50)
    provider_user_id: str = Field(min_length=1, max_length=100)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
        ),
    )
