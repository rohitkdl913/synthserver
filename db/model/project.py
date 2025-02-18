from typing import List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .subtitle import Subtitle  # Only imported for type checking

class Project(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    translationType: str
    status: bool  # This represents if the project is completed or not
    video_file: str
    thumbnail_file: str
    
    subtitles: List["Subtitle"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
