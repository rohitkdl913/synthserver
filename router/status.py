import asyncio
import json
import queue
import logging

from fastapi.responses import StreamingResponse
from ..db.db import dbManagerDep,dbManager
from fastapi import APIRouter
from ..utils import get_project_subtitle_path
from ..queue_manager import sseQueueManager,queueManager
from sse_starlette.sse import EventSourceResponse

router= APIRouter(
    prefix="/project",
    tags=["Project Status Pooling"],
    responses={404: {"description": "Not found"}},
)


def read_subtitle_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data 

logger = logging.getLogger('uvicorn.error')


@router.get("/status/{id}")
async def get_status(id:str,dbManager:dbManagerDep):
    project= dbManager.get_project_by_id(id)
    if project == None:
        return 400, {"Message": "There is no project of id", "data":None}
   
    if project.status ==True:
        data= dbManager.get_subtitles_by_project(id)
        return {"Message": "Successfully transcribed!", "data": {"id": id,"name":project.name,"translationType":project.translationType,"status":project.status,"subtitle":data}}
    else:
        return {"Message": "Pending yet not transcribed", "data": {"id":id,"name":project.name,"translationType":project.translationType,"status":project.status,"subtitle":None}}

MESSAGE_STREAM_DELAY = 1  # second
MESSAGE_STREAM_RETRY_TIMEOUT = 15000  # milisecond

async def event_generator(project_id: str):
    
    project = dbManager.get_project_by_id(project_id)
    if project is None:
        yield {
            "event": "error",
            "data": "Project not found"
        }
        return
    
    if project.status:
        yield {
            "event": "done",
            "data": "done"
        }
        return
    
    if not sseQueueManager.isProjectInQueue(project_id=project_id):
        yield {
            "event": "done",
            "data": "Project not found"
        }
        dbManager.update_project_status(project_id,True)
        return
        
    while True:
        try:
            subtitle = await sseQueueManager.getFromQueue(project_id)
           
            if subtitle is None:
                logger.debug(" I am done with transcribtion")
                print(" I am done with transcribtion")
                yield {
                    "event": "done",
                    "id": "message_id",
                    "retry": MESSAGE_STREAM_RETRY_TIMEOUT,
                    "data": 'done',
                } 
                
                break
            
            subtitle={
                "id":subtitle.id,
                "text":subtitle.text,
                "start":subtitle.start_time,
                "end":subtitle.end_time
            }   
            # Proper SSE formatting
            # yield f"event: update\ndata: {subtitle.model_dump_json()} \n\n"
            logger.debug(f" I am updating  transcribtion {subtitle}")
            print(f" I am updating  transcribtion {subtitle}")
            yield  {
                    "event": "update",
                    "id": "message_id",
                    "retry": MESSAGE_STREAM_RETRY_TIMEOUT,
                    "data": f'{json.dumps(subtitle,indent=4)}',
                }  
            
        except asyncio.TimeoutError:
            # yield "event: status\nkeep-alive \n\n"
            logger.debug("Keep alive the connection")
            print("Keep alive the connection")
            yield  {
                    "event": "open",
                    "id": "message_id",
                    "retry": MESSAGE_STREAM_RETRY_TIMEOUT,
                    "data": "keep-alive",
                } 
        await asyncio.sleep(MESSAGE_STREAM_DELAY)
        

@router.get("/stream/{project_id}")
async def stream_transcription(project_id: str):
    """ SSE endpoint to stream transcription updates. """
    return EventSourceResponse(
        event_generator(project_id)
    )


@router.get("/")
async def get_projects(dbManager:dbManagerDep):
    projects= dbManager.get_all_project()
    # Filter out media-related fields from project data
    filtered_projects = [
        {
            "id": p.id,
            "name": p.name,
            "translationType": p.translationType,
            "status": p.status,
            "updatedAt": p.updated_at,
            "createdAt": p.created_at
        } 
        for p in projects
    ]
    return {
        "Message": "Success",
        "data": filtered_projects
    }


@router.get("/recent")
async def get_recent_projects(dbManager: dbManagerDep):
    projects = dbManager.get_all_project()
    recent_projects = sorted(projects, key=lambda p: p.updated_at, reverse=True)
    
    recent_projects = recent_projects[:3]
    
    filtered_projects = [
        {
            "id": p.id,
            "name": p.name,
            "translationType": p.translationType,
            "status": p.status,
            "updatedAt": p.updated_at,
            "createdAt": p.created_at
        }
        for p in recent_projects
    ]
    
    return {
        "Message": "Recent projects retrieved successfully",
        "data": filtered_projects
    }
