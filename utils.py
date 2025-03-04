import os
import shutil

import ffmpeg

from .db.db import dbManager
def get_project_path(projectId:str)->str:
    projectsPath=os.path.join("projects", f"{projectId}")
    return projectsPath
    
def get_project_video_path(projecId:str)->str:
    project=dbManager.get_project_by_id(projectId=projecId)
    projectPath= get_project_path(projectId=projecId)
    videoPath= os.path.join(projectPath,"media",project.video_file)
    return videoPath
    
def get_project_audio_path(projecId:str)->str:
    project=dbManager.get_project_by_id(projectId=projecId)
    projectPath= get_project_path(projectId=projecId)
    audioPath= os.path.join(projectPath,"media","audio.mp3")
    return audioPath

def get_project_subtitle_path(projecId:str)->str:
    projectPath= get_project_path(projectId=projecId)
    subtitlePath= os.path.join(projectPath,"subtitle.json")
    return subtitlePath

def get_project_thumbnail_path(projecId:str)->str:
    projectPath= get_project_path(projectId=projecId)
    videoPath= os.path.join(projectPath,"media","thumbnail.jpg")
    return videoPath


def delete_directory(directory_path: str):
    if os.path.exists(directory_path):
        try:
            shutil.rmtree(directory_path)
            print(f"Directory '{directory_path}' has been deleted successfully.")
        except Exception as e:
            print(f"Error occurred while deleting directory: {e}")
    else:
        print(f"Directory '{directory_path}' does not exist.")

def write_to_file(dict:str):
    with open("transcribtion.json","+w") as file:
        file.write(dict)
    
   
def batch_word_timestamp(size:int,data:dict,duration:float)->list: 
    # Extract words from segments
    words_list = [
        word for segment in data['segments'] for word in segment['words']
        if word['start'] <= duration
    ]
    size = 10

    # Process chunks and build final output
    final_output = [
        {
            "start": chunk[0]['start'],
            "end": chunk[-1]['end'],
            "text": ' '.join(word['word'] for word in chunk)
        }
        for i in range(0, len(words_list), size)
        if (chunk := words_list[i:i + size])
    ]
    return final_output
        
def get_video_duration(file_path:str):
    probe = ffmpeg.probe(file_path)
    duration = float(probe['format']['duration'])
    return duration