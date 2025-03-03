import json
import os
from google import genai
from dotenv import load_dotenv
from fastapi import APIRouter

from ..db.model.subtitle import Subtitle
from ..db.db import dbManagerDep


load_dotenv()


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


def generate_prompt(subtitles:list[Subtitle])->str:
    subtitle_sanitized:list[dict] =[{"id": subtitle.id,"start_time":subtitle.start_time,"end_time":subtitle.end_time,"text":subtitle.text} for subtitle in subtitles]
    subtitle_sanitized_str= json.dumps(subtitle_sanitized)
    prompt=""" 
        For the following Nepali transciption of audio with timestamp, first read all the text contents and understand the context and correct and then modify the text such as correct nepali word spellings, punctuations,etc .Do not modify the structure and original meaning of the text and return json with same structure with correction:
    """
    final_prompt_with_subtitle=prompt+ subtitle_sanitized_str
    return final_prompt_with_subtitle
    
def get_ai_response(prompt:str)->str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt)
    return response.text



router = APIRouter(
    prefix="/ai",
    tags=["Recreate with ai"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{projectId}")
async def recreate_with_ai(projectId:str,dbManager: dbManagerDep,):
    project= dbManager.get_project_by_id(projectId=projectId)
    if project == None:
        return 400, {"Message": "There is no project of id", "data":None}
   
    if project.status ==True:
        data= dbManager.get_subtitles_by_project(project_id=projectId)
        prompt= generate_prompt(data)
        response= get_ai_response(prompt=prompt)
        response= response[7:]
        response= response[:-3]
        print(f"Response from gemini {response}")
        response:list[dict] = json.loads(response)
        print(f"Decoded response:{response}")
        
        for subtitle in response:
            dbManager.update_subtitle(subtitle_id=subtitle["id"],start_time=subtitle["start_time"],end_time=subtitle["end_time"],text=subtitle["text"])
            
        return {"Message": "Successfully transcribed!", "data": {"id": projectId,"name":project.name,"translationType":project.translationType,"status":project.status,"subtitle":response}}
    else:
        return {"Message": "Pending yet not transcribed", "data": {"id":projectId,"name":project.name,"translationType":project.translationType,"status":project.status,"subtitle":None}}
    
    

