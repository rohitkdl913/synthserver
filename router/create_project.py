import json
import math
import os
import asyncio
import uuid
import aiofiles
import ffmpeg
from typing import Annotated
from fastapi import APIRouter, Body, Depends, File, Form, UploadFile, HTTPException
from pydantic import BaseModel

from ..utils import get_video_duration

from ..router.middleware.get_user_email import get_current_user

from ..db.db import dbManagerDep
from ..queue_manager import QueuingItem, queueManager,sseQueueManager

router = APIRouter(
    prefix="/create-project",
    tags=["Project Creation"],
    responses={404: {"description": "Not found"}},
)

# Allowed video formats
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'flv', 'webm', 'wmv'}
DEFAULT_THUMBNAIL = "thumbnail.jpg"

class CreateProjectRequestModel(BaseModel):
    projectName: str
    translationType: str = "BULK"

class SettingsModel:
    def __init__(self, projectId: str, projectName: str, translationType: str):
        self.projectId = projectId
        self.projectName = projectName
        self.translationType = translationType

@router.post("/")
async def create_project(
    dbManager: dbManagerDep,
    project_setting: str = Form(...),
    in_file: UploadFile = File(...),
    email: str = Depends(get_current_user)
):
    # Validate file format
    file_ext = os.path.splitext(in_file.filename)[1][1:].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, detail="Unsupported file format")

    unique_id = uuid.uuid4().hex
    settings = CreateProjectRequestModel.parse_raw(project_setting)
    
    # Create project structure and get file info
    video_file, thumbnail_file,video_duration = await create_project_template(
        in_file,
        SettingsModel(
            projectId=unique_id,
            projectName=settings.projectName,
            translationType=settings.translationType
        )
    )
    
    
    
    # Store in database with file info
    new_project= dbManager.add_projects(
        projectName=settings.projectName,
        projectId=unique_id,
        translationType=settings.translationType,
        video_file=video_file,
        thumbnail_file=thumbnail_file,
        user_email=email,
        video_duration=math.floor(video_duration)
    )
    #send the true video duration to model for proper processing of subtitle
    queueManager.put_nowait(QueuingItem(project_id=unique_id,video_duration=video_duration))
    
    
    sseQueueManager.initialize_queue(unique_id)
    
    return {"Message": "Successfully loaded in queue", "data": {
            "id": new_project.id,
            "name": new_project.name,
            "translationType": new_project.translationType,
            "status": new_project.status,
            "updatedAt": new_project.updated_at,
            "createdAt": new_project.created_at,
            "duration":new_project.video_duration
        } }
    
    
    
    

async def create_project_template(uploaded_file: UploadFile, settings: SettingsModel):
    base_dir = os.path.join(os.getcwd(), "projects", settings.projectId)
    media_dir = os.path.join(base_dir, "media")
    
    # Create directories
    os.makedirs(media_dir, exist_ok=True)

    # Save video with original extension
    video_filename = f"video_{uuid.uuid4().hex}.{os.path.splitext(uploaded_file.filename)[1][1:]}"
    video_path = os.path.join(media_dir, video_filename)
    
    # Save video file
    async with aiofiles.open(video_path, 'wb') as out_file:
        while content := await uploaded_file.read(1024):
            await out_file.write(content)
    
    
    #Get the video duration
    video_duration=get_video_duration(video_path)
    
    

    # Generate thumbnail
    thumbnail_filename = DEFAULT_THUMBNAIL
    thumbnail_path = os.path.join(media_dir, thumbnail_filename)
    
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: (
                ffmpeg.input(video_path)
                .filter('scale', 320, -1)
                .output(thumbnail_path, vframes=1, ss='00:00:01')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        )
        
    except ffmpeg.Error as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        thumbnail_filename = None  # Or set default thumbnail path

    # Create settings.json
    setting_json = {
        "id": settings.projectId,
        "projectName": settings.projectName,
        "videoFile": video_filename,
        "videoDuration": video_duration,
        "thumbnailFile": thumbnail_filename,
        "mediaPath": "media",
        "translationType": settings.translationType
    }

    setting_path = os.path.join(base_dir, "settings.json")
    async with aiofiles.open(setting_path, 'w') as setting_file:
        await setting_file.write(json.dumps(setting_json, indent=4))

    print(f"Project structure created at: {base_dir}")
    return video_filename, thumbnail_filename,video_duration