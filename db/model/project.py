import datetime
from typing import List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from .subtitle import Subtitle  # Only imported for type checking
    from .user import User
    
    
    
class Project(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    translationType: str
    status: bool  # This represents if the project is completed or not
    video_file: str
    thumbnail_file: str
    
    video_duration: int
    
    subtitles: List["Subtitle"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    
    user_email: str = Field(foreign_key="user.email")
    
    user: "User" = Relationship(back_populates="projects")
    
    
    created_at: datetime.datetime = Field(default_factory=lambda : datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda : datetime.datetime.now(datetime.timezone.utc), nullable=True)
    
    
    def update_project_updated_at(self):
        self.updated_at = datetime.datetime.now(datetime.timezone.utc)