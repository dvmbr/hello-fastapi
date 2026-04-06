from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint
from sqlmodel import Field, SQLModel


class MentoringPostTopic(SQLModel, table=True):
    __tablename__ = "mentoring_post_topics"
    __table_args__ = (
        PrimaryKeyConstraint(
            "mentoring_post_id", "topic_id", name="pk_mentoring_post_topics"
        ),
    )

    mentoring_post_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("mentoring_posts.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    topic_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
        )
    )
