from multiprocessing import Process
from fastapi import FastAPI
import threading


from .worker import worker
from .router import create_project,status,export,stream,delete_project,subtitle

from fastapi.middleware.cors import CORSMiddleware

from .queue_manager import sseQueueManager
from .db.db import dbManager


# Start worker process
threading.Thread(target=worker, daemon=True).start()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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






