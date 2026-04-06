from sqlalchemy import Column, ForeignKey, Index, Integer, PrimaryKeyConstraint
from sqlmodel import Field, SQLModel


class MentoringPostTopic(SQLModel, table=True):
    __tablename__ = "mentoring_post_topics"
    __table_args__ = (
        # 복합 PK: 한 멘토링 글과 한 토픽의 조합이 유일하도록 보장 (중복 방지, N:M 관계의 표준)
        PrimaryKeyConstraint(
            "mentoring_post_id", "topic_id", name="pk_mentoring_post_topics"
        ),
        # topic_id 인덱스: 특정 토픽에 연결된 모든 멘토링 글을 빠르게 조회할 때 사용
        # 예) SELECT * FROM mentoring_post_topics WHERE topic_id = ...
        Index("ix_mentoring_post_topics_topic_id", "topic_id"),
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
