from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db.model.subtitle import Subtitle
from ..db.db import dbManagerDep


router = APIRouter(
     prefix="/subtitle",
    tags=["Subtitle CRUD"],
    responses={404: {"description": "Not found"}},
)

class SubtitleCreate(BaseModel):
    project_id: str
    language: str
    start_time: int
    end_time: int
    text: str


@router.post("/", response_model=Subtitle)
def create_subtitle(subtitle: SubtitleCreate, db: dbManagerDep):
    if not db.is_project_available(subtitle.project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return db.add_subtitle(
        subtitle.project_id, subtitle.language, subtitle.start_time, subtitle.end_time, subtitle.text
    )

@router.put("/{subtitle_id}", response_model=Subtitle)
def update_subtitle(subtitle_id: int, subtitle_update: Subtitle, db: dbManagerDep):
    subtitle = db.update_subtitle(subtitle_id, subtitle_update.text)
    if not subtitle:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    return subtitle

@router.delete("/{subtitle_id}", response_model=dict)
def delete_subtitle(subtitle_id: int, db: dbManagerDep):
    with db.engine.begin() as session:
        subtitle = session.get(Subtitle, subtitle_id)
        if not subtitle:
            raise HTTPException(status_code=404, detail="Subtitle not found")
        session.delete(subtitle)
        session.commit()
    return {"message": "Subtitle deleted successfully"}