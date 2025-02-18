from fastapi import APIRouter
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from ..db.db import dbManagerDep
from ..utils import get_project_path

import shutil
import os
import tempfile

def compress_to_zip(folder_path: str) -> str:
    """Compresses a folder into a temporary ZIP file."""
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    temp_zip.close()  # Close the file to prevent conflicts

    zip_path = shutil.make_archive(temp_zip.name[:-4], 'zip', folder_path)  # Remove .zip suffix
    return zip_path  # Return final zip file path

router = APIRouter(
    prefix="/export",
    tags=["Project Export"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{id}")
async def export_project(id: str, dbManager: dbManagerDep):
    project = dbManager.get_project_by_id(id)
    
    if project is None:
        return JSONResponse(status_code=400, content={"message": "Project ID not found", "data": None})

    project_path = get_project_path(id)
    temp_project_zip = compress_to_zip(project_path)

    def iterfile():
        """Streams the ZIP file in chunks to prevent high memory usage."""
        with open(temp_project_zip, "rb") as file_like:
            while chunk := file_like.read(1024 * 1024):  # Read in 1MB chunks
                yield chunk
        os.remove(temp_project_zip)  # Cleanup after sending

    return StreamingResponse(
        iterfile(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={project.name}.zip"}
    )



def format_timestamp(ms: int) -> str:
    """Converts milliseconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


@router.get("/subtitle/{id}")
async def export_subtitle(id:str,dbManager: dbManagerDep):
    subtitles = dbManager.get_subtitles_by_project(id)
    
    if not subtitles:
        return JSONResponse(status_code=400, content={"message": "No subtitles found for this project", "data": None})

    # Generate SRT content
    srt_content = ""
    for i, subtitle in enumerate(subtitles, start=1):
        start_time = format_timestamp(subtitle.start_time)
        end_time = format_timestamp(subtitle.end_time)
        srt_content += f"{i}\n{start_time} --> {end_time}\n{subtitle.text}\n\n"

    # Save to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".srt")
    temp_file.write(srt_content.encode("utf-8"))
    temp_file.close()

    return FileResponse(
        temp_file.name,
        media_type="text/plain",
        filename=f"{id}.srt"
    )