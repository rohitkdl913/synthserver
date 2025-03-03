import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel, Session

if TYPE_CHECKING:
    from .project import Project  



class Subtitle(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    project_id: str = Field(foreign_key="project.id")
    language: str = Field(max_length=10)
    start_time: int 
    end_time: int 
    text: str
    
    project: "Project" = Relationship(back_populates="subtitles")

    created_at: datetime.datetime = Field(default_factory=lambda : datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda : datetime.datetime.now(datetime.timezone.utc),nullable=True)
    
    
    def update_updated_at(self, session:Session):
        self.updated_at = datetime.datetime.utcnow()
        session.commit()
        
        project = self.project
        project.update_project_updated_at()
        session.commit()