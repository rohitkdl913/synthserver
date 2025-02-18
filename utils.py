import os
import shutil

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
