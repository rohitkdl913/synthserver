import os
import aiofiles
import aiofiles.os
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse, Response

from ..db.db import dbManagerDep
from ..utils import get_project_thumbnail_path, get_project_video_path

router = APIRouter(
    prefix="/stream",
    tags=["Stream"],
    responses={404: {"description": "Not found"}},
)

CHUNK_SIZE = 1024 * 1024  # 1MB chunks


@router.get("/video/{id}")
async def stream_video(id: str, request: Request, dbManager: dbManagerDep):
    if not dbManager.is_project_available(id):
        return Response(status_code=400, content="Project ID not found")

    video_path = get_project_video_path(id)
    print(f"Video path is {video_path}")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    file_size = os.stat(video_path).st_size
    range_header = request.headers.get("range")

    async def iterfile(start: int, end: int):
        with open(video_path, "rb") as file:
            file.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = file.read(min(CHUNK_SIZE, remaining))
                if not chunk:
                    break
                yield chunk
                remaining -= len(chunk)

    if range_header:
        # Handle partial content request
        try:
            range_val = range_header.replace("bytes=", "").strip()
            start, end = range_val.split("-")
            start = int(start)
            end = int(end) if end else file_size - 1
            # Ensure end does not exceed file size
            end = min(end, file_size - 1)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid range header")

        content_length = end - start + 1
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": "video/mp4",
        }
        return StreamingResponse(iterfile(start, end), headers=headers, status_code=206)

    # Full file request (e.g., direct link)
    headers = {
        "Content-Length": str(file_size),
        "Content-Type": "video/mp4",
        "Accept-Ranges": "bytes",
    }
    return StreamingResponse(iterfile(0, file_size - 1), headers=headers, status_code=200)




@router.get("/thumbnail/{id}")
async def stream_thumbnail(id: str, request: Request, dbManager: dbManagerDep):
    # Validate project exists
    if not dbManager.is_project_available(id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST, 
                      content="Invalid project ID")

    thumbnail_path = get_project_thumbnail_path(id)
    # # Security checks
    if not os.path.exists(thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail file missing")
    
    if not os.path.isfile(thumbnail_path):
        raise HTTPException(status_code=422, detail="Invalid thumbnail path")

    # Get file stats and determine content type
    file_size = os.stat(thumbnail_path).st_size
    file_ext = os.path.splitext(thumbnail_path)[1].lower()
    content_type = "image/jpeg"  # Default based on your thumbnail format
    
    # Range header handling for partial content
    range_header = request.headers.get("range")
    

    def file_iterator(start: int = 0, end: int = None):
        end = end or file_size - 1
        with open(thumbnail_path, "rb") as file:
            file.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = file.read(min(CHUNK_SIZE, remaining))
                if not chunk:
                    break
                yield chunk
                remaining -= len(chunk)

    if range_header:
        try:
            range_val = range_header.replace("bytes=", "").strip()
            start_str, end_str = range_val.split("-")
            start = int(start_str)
            end = int(end_str) if end_str else file_size - 1
            end = min(end, file_size - 1)
        except (ValueError, TypeError):
            raise HTTPException(status_code=416, detail="Invalid range header")

        content_length = end - start + 1
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": content_type,
        }
        return StreamingResponse(
            file_iterator(start, end),
            headers=headers,
            status_code=206
        )

    # Full file response headers
    headers = {
        "Content-Length": str(file_size),
        "Content-Type": content_type,
        "Accept-Ranges": "bytes",
        "Cache-Control": "public, max-age=604800"  # 1 week cache
    }

    return StreamingResponse(
        file_iterator(0, file_size - 1),
        headers=headers,
        status_code=200
    )


# import aiofiles
# import aiofiles.os
# from fastapi import APIRouter, HTTPException, Request, status
# from fastapi.responses import StreamingResponse, Response
# from ..db.db import dbManagerDep
# from ..utils import get_project_thumbnail_path, get_project_video_path

# router = APIRouter(
#     prefix="/stream",
#     tags=["Stream"],
#     responses={404: {"description": "Not found"}},
# )

# CHUNK_SIZE = 1024 * 1024  # 1MB chunks


# @router.get("/video/{id}")
# async def stream_video(id: str, request: Request, dbManager: dbManagerDep):
#     if not dbManager.is_project_available(id):
#         return Response(status_code=400, content="Project ID not found")

#     video_path = get_project_video_path(id)
#     if not await aiofiles.os.path.exists(video_path):
#         raise HTTPException(status_code=404, detail="Video file not found")

#     file_stat = await aiofiles.os.stat(video_path)
#     file_size = file_stat.st_size
#     range_header = request.headers.get("range")

#     async def iterfile(start: int, end: int):
#         async with aiofiles.open(video_path, "rb") as file:
#             await file.seek(start)
#             remaining = end - start + 1
#             while remaining > 0:
#                 chunk = await file.read(min(CHUNK_SIZE, remaining))
#                 if not chunk:
#                     break
#                 yield chunk
#                 remaining -= len(chunk)

#     if range_header:
#         try:
#             range_val = range_header.replace("bytes=", "").strip()
#             start, end = range_val.split("-")
#             start = int(start)
#             end = int(end) if end else file_size - 1
#             end = min(end, file_size - 1)
#         except ValueError:
#             raise HTTPException(status_code=400, detail="Invalid range header")

#         content_length = end - start + 1
#         headers = {
#             "Content-Range": f"bytes {start}-{end}/{file_size}",
#             "Accept-Ranges": "bytes",
#             "Content-Length": str(content_length),
#             "Content-Type": "video/mp4",
#         }
#         return StreamingResponse(iterfile(start, end), headers=headers, status_code=206)

#     headers = {
#         "Content-Length": str(file_size),
#         "Content-Type": "video/mp4",
#         "Accept-Ranges": "bytes",
#     }
#     return StreamingResponse(iterfile(0, file_size - 1), headers=headers, status_code=200)


# @router.get("/thumbnail/{id}")
# async def stream_thumbnail(id: str, request: Request, dbManager: dbManagerDep):
#     if not dbManager.is_project_available(id):
#         return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid project ID")

#     thumbnail_path = get_project_thumbnail_path(id)
#     if not await aiofiles.os.path.exists(thumbnail_path):
#         raise HTTPException(status_code=404, detail="Thumbnail file missing")

#     if not await aiofiles.os.path.isfile(thumbnail_path):
#         raise HTTPException(status_code=422, detail="Invalid thumbnail path")

#     file_stat = await aiofiles.os.stat(thumbnail_path)
#     file_size = file_stat.st_size
#     file_ext = thumbnail_path.split(".")[-1].lower()
#     content_type = "image/jpeg"  # Default type

#     range_header = request.headers.get("range")

#     async def file_iterator(start: int, end: int):
#         async with aiofiles.open(thumbnail_path, "rb") as file:
#             await file.seek(start)
#             remaining = end - start + 1
#             while remaining > 0:
#                 chunk = await file.read(min(CHUNK_SIZE, remaining))
#                 if not chunk:
#                     break
#                 yield chunk
#                 remaining -= len(chunk)

#     if range_header:
#         try:
#             range_val = range_header.replace("bytes=", "").strip()
#             start_str, end_str = range_val.split("-")
#             start = int(start_str)
#             end = int(end_str) if end_str else file_size - 1
#             end = min(end, file_size - 1)
#         except (ValueError, TypeError):
#             raise HTTPException(status_code=416, detail="Invalid range header")

#         content_length = end - start + 1
#         headers = {
#             "Content-Range": f"bytes {start}-{end}/{file_size}",
#             "Accept-Ranges": "bytes",
#             "Content-Length": str(content_length),
#             "Content-Type": content_type,
#         }
#         return StreamingResponse(file_iterator(start, end), headers=headers, status_code=206)

#     headers = {
#         "Content-Length": str(file_size),
#         "Content-Type": content_type,
#         "Accept-Ranges": "bytes",
#         "Cache-Control": "public, max-age=604800",
#     }
#     return StreamingResponse(file_iterator(0, file_size - 1), headers=headers, status_code=200)