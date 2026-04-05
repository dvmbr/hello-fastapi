from sqlmodel import Field, SQLModel


class JobPostTag(SQLModel, table=True):
    __tablename__ = "job_post_tags"

    job_post_id: int = Field(foreign_key="job_posts.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)