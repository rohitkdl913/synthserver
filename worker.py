import asyncio
import json

from .utils import get_project_audio_path, get_project_subtitle_path, get_project_video_path


from .translator import Translator
from .queue_manager import queueManager,sseQueueManager
from .db.db import dbManager


import ffmpeg

def convert_video_to_audio(input_video, output_audio):
    ffmpeg.input(input_video).output(output_audio, format='mp3', acodec='libmp3lame').run()


#This is the main worker thread responsible for converting the audio to subtitle
def worker():
    translator= Translator("./whisper-model.pt")
    while True:
        item = queueManager.get()
        print(f'Working on {item.project_id}')
        print(f'Finished {item.project_id}')
        
        videoPath= get_project_video_path(item.project_id)
        audioPath= get_project_audio_path(item.project_id)
        subtitlePath= get_project_subtitle_path(item.project_id)
        convert_video_to_audio(input_video=videoPath,output_audio=audioPath)
        
        # asyncio.run(translator.transcribe_realtime(audioPath=audioPath,projectId=item))
        asyncio.run(translator.transcribe(item.project_id,audioPath,video_duration=item.video_duration))
        dbManager.update_project_status(item.project_id,True)
        



