from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..db.model.subtitle import Subtitle
from ..db.db import dbManagerDep


router = APIRouter(
     prefix="/subtitle",
    tags=["Subtitle CRUD"],
    responses={404: {"description": "Not found"}},
)
class SubtitleUpdate(BaseModel):
    id: int
    start: int
    end: int
    text: str
    language: str


class SubtitleCreate(BaseModel):
    id:str #This is project id
    start: int
    end: int
    text: str
    language: str


@router.post("/")
def create_subtitle(subtitle: SubtitleCreate, db: dbManagerDep):
    if not db.is_project_available(subtitle.id):
        raise HTTPException(status_code=404, detail="Project not found")
    return db.add_subtitle(
        subtitle.id, subtitle.language, subtitle.start, subtitle.end, subtitle.text
    )

@router.put("/{subtitle_id}")
def update_subtitle(subtitle_id: int, subtitle_update: SubtitleUpdate, db: dbManagerDep):
    subtitle = db.update_subtitle(subtitle_id, start_time=subtitle_update.start,end_time=subtitle_update.end,text=subtitle_update.text,language=subtitle_update.language)
    print(f"To update subtitle:{subtitle_update.start} and {subtitle_update.end}")
    if not subtitle:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    return subtitle

@router.delete("/{subtitle_id}")
def delete_subtitle(subtitle_id: int, db: dbManagerDep):
    status= db.delete_subtitle(subtitle_id=subtitle_id)
    if status:
        return JSONResponse( {"Message": "Subtitle deleted successfully","data":None},status_code=200)
    else:
        return JSONResponse( {"Message": "Something error occured while deleting","data":None},status_code=400)
    