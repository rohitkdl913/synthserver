from multiprocessing import Process
from fastapi import FastAPI
import threading


from .worker import worker
from .router import create_project,status,export,stream,delete_project,subtitle,ai,auth

from fastapi.middleware.cors import CORSMiddleware

from .queue_manager import sseQueueManager
from .db.db import dbManager


# Start worker process
threading.Thread(target=worker, daemon=True).start()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://013a-2400-1a00-bd11-8fe9-4793-ba93-21f6-563f.ngrok-free.app","https://33cc-2400-1a00-bd11-8fe9-4793-ba93-21f6-563f.ngrok-free.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(create_project.router)
app.include_router(status.router)
app.include_router(export.router)
app.include_router(stream.router)
app.include_router(delete_project.router)
app.include_router(subtitle.router)
app.include_router(ai.router)
app.include_router(auth.router)








