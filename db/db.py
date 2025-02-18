from typing import Annotated, List
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine, select

from .model.subtitle import Subtitle
from .model.project import Project

sqlite_file_name = "db/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

class DBManager:
    def __init__(self):
        self.connect_args = {"check_same_thread": False}
        self.engine = create_engine(sqlite_url, connect_args=self.connect_args)
        SQLModel.metadata.create_all(self.engine)
        
    def add_projects(self, projectName: str, projectId: str, translationType: str, 
                video_file: str, thumbnail_file: str):
        with Session(self.engine) as session:
            project = Project(
                id=projectId,
                name=projectName,
                translationType=translationType,
                status=False,
                video_file=video_file,
                thumbnail_file=thumbnail_file
            )
            session.add(project)
            session.commit()
    
    def check_project_status(self,projectId:str)->bool | None:
        with Session(self.engine) as session:
            projects= session.get(Project,projectId)
            if projects ==None:
                return None
            return projects.status
        
    def update_project_status(self,projectId:str,status:bool):
        with Session(self.engine) as session:
            projects= session.get(Project,projectId)
            if projects ==None:
                return None
            
            setattr(projects,"status",status)
            session.commit()
            session.refresh(projects)
    
    def is_project_available(self,projectId:str)->bool:
        with Session(self.engine) as session:
            project= session.get(Project, projectId)
            if project != None: return True
            return False
        
    def get_project_by_id(self,projectId:str)->Project:
        with Session(self.engine) as session:
            project= session.get(Project,projectId)
            return project
    
    def get_all_project(self)->list[Project]:
        with Session(self.engine) as session:
            projects = session.exec(select(Project)).all()
            return projects
    
    def add_subtitle(self, project_id: str, language: str, start_time: int, end_time: int, text: str):
        with Session(self.engine) as session:
            subtitle = Subtitle(project_id=project_id, language=language, start_time=start_time, end_time=end_time, text=text)
            session.add(subtitle)
            session.commit()
            session.refresh(subtitle)
            return subtitle

    def get_subtitles_by_project(self, project_id: str) -> List[Subtitle]:
        with Session(self.engine) as session:
            subtitles = session.exec(select(Subtitle).where(Subtitle.project_id == project_id)).all()
            return subtitles

    def update_subtitle(self, subtitle_id: int, text: str):
        with Session(self.engine) as session:
            subtitle = session.get(Subtitle, subtitle_id)
            if subtitle:
                subtitle.text = text
                session.commit()
                session.refresh(subtitle)
                return subtitle
            return None
    def delete_project(self,project_id:str)->bool:
        with Session(self.engine) as session:
            # Fetch the project by ID
            project = session.get(Project, project_id)
            
            if project:
                # Delete associated subtitles first (optional: ensure cascading delete)
                session.exec(select(Subtitle).where(Subtitle.project_id == project_id))
                session.commit()

                # Delete the project
                session.delete(project)
                session.commit()
                return True
            return False

dbManager = DBManager()       
def get_DbManager()->DBManager:
    return dbManager

dbManagerDep = Annotated[DBManager, Depends(get_DbManager)]
