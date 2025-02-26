
import json
import numpy as np
import whisper
from pydub import AudioSegment, silence

from .utils import batch_word_timestamp, write_to_file

from .db.model.subtitle import Subtitle
from .queue_manager import sseQueueManager

from .db.db import dbManager
import torch

# Audio processing parameters
MIN_SILENCE_LEN = 700  # Min silence duration (ms) to split audio
SILENCE_THRESH = -40  # Silence threshold in dBFS
SAMPLE_RATE = 16000  # Whisper expects 16kHz audio


device= "cuda" if torch.cuda.is_available() else "cpu"





class Translator:
    def __init__(self,modelName:str):
        self.modelName= modelName
        self.model= whisper.load_model(modelName)

    async def transcribe(self,projectId:str,audioPath:str):
        result = self.model.transcribe(audioPath,word_timestamps=True)
        # print(f"{result}")
        # write_to_file(json.dumps(result))
        
        # segments= result["segments"]
        # words_list = [ word for word in segment["words"] for segment in segments]
       
        # for idx,single_word in enumerate(words_list):
        segments= batch_word_timestamp(size=10,data=result)
        for segment in segments:                        
                dbManager.add_subtitle(project_id=projectId,start_time=segment["start"],end_time=segment["end"],text=segment["text"],language="nepali")
                # await sseQueueManager.sendToQueue(projectId,Subtitle(project_id=projectId,start_time=segment["start"],end_time=segment["end"],text=segment["text"],language="nepali"))
        await sseQueueManager.sendToQueue(projectId,None)    
    
    async def transcribe_realtime(self,projectId:str,audioPath:str):
        """Process the audio file and transcribe it in real-time chunks."""
        print(f"Processing: {audioPath}")

        # Load audio file and convert it to 16kHz mono
        audio = AudioSegment.from_file(audioPath).set_frame_rate(SAMPLE_RATE).set_channels(1)

        # Split based on silence
        chunks = silence.split_on_silence(audio, min_silence_len=MIN_SILENCE_LEN, silence_thresh=SILENCE_THRESH)

        for i, chunk in enumerate(chunks):
            # Ensure the chunk is at least 1 second long for Whisper to work properly
            if len(chunk) < 5000:
                chunk = chunk + AudioSegment.silent(duration=1000 - len(chunk))

            # Convert chunk to numpy array compatible with Whisper
            samples = np.array(chunk.get_array_of_samples())
            
            # Normalize to float32 in [-1, 1] range
            samples = samples.astype(np.float32) / (2 ** (8 * chunk.sample_width - 1))

            # Use Whisper's built-in transcribe function
            result = self.model.transcribe(samples, fp16=False)
            segments = result["segments"]
            print(f"Chunk {i+1}: {segments}")
            for segment in segments:
                dbManager.add_subtitle(project_id=projectId,start_time=segment["start"],end_time=segment["end"],text=segment["text"],language="nepali")
                await sseQueueManager.sendToQueue(projectId,Subtitle(project_id=projectId,start_time=segment["start"],end_time=segment["end"],text=segment["text"],language="nepali"))
        await sseQueueManager.sendToQueue(projectId,None)    
            

              
                
