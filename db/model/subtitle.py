from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .project import Project  # Only imported for type checking

class Subtitle(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    project_id: str = Field(foreign_key="project.id")
    language: str = Field(max_length=10)
    start_time: float 
    end_time: float 
    text: str
    
    project: "Project" = Relationship(back_populates="subtitles")
