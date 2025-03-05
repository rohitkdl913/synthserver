from queue import Queue
from typing import Optional
from .db.model.subtitle import Subtitle
import asyncio




class QueuingItem:   
    def __init__(self, project_id: str,video_duration:float):
        self.project_id = project_id
        self.video_duration = video_duration
    
    


#For now we can simply use raw queue for queuing the work
queueManager:Queue[QueuingItem] = Queue()



    




class SSEQueueManager:
    def __init__(self):
        self.queues:dict[str:asyncio.Queue] = {}

    def initialize_queue(self, project_id: str):
        if project_id not in self.queues:
            self.queues[project_id] = asyncio.Queue()
     # Add this method to check queue existence
    def queue_exists(self, project_id: str) -> bool:
        return project_id in self.queues
    
    
    async def getFromQueue(self, project_id: str) -> Optional[Subtitle]:
        return await asyncio.wait_for(self.queues[project_id].get(), timeout=10.0)
       

    async def sendToQueue(self, project_id: str, data: Subtitle | None):
        if project_id not in self.queues:
            self.initialize_queue(project_id)
        await self.queues[project_id].put(data)
    
    def isProjectInQueue(self, project_id:str)->bool:
        return project_id in self.queues

sseQueueManager = SSEQueueManager()