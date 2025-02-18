import os
from fastapi import APIRouter

from ..utils import delete_directory, get_project_path
from ..db.db import dbManagerDep

router = APIRouter(
    prefix="/delete",
    tags=["Project Creation"],
    responses={404: {"description": "Not found"}},
)

@router.delete("/project/{id}")
async def delete_project(id:str, dbManager: dbManagerDep):
    if dbManager.delete_project(id):
        project_path= get_project_path(id)
        delete_directory(project_path)
        return {"Message":"Successfull","data":None}
    return {"Message":"Cannot delete the account","data":None}
    
    