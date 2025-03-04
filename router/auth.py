import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from pydantic import BaseModel


from ..router.middleware.get_user_email import get_current_user
from ..router.utils.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

from ..db.db import dbManagerDep
from ..db.model.user import pwd_context


router = APIRouter(
    prefix="/auth",
    tags=["User Authentication"],
    responses={404: {"description": "Not found"}},
)



class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str
    
    

    
    
@router.post("/signup")
def signup(request: SignupRequest, dbManager: dbManagerDep):
    try:
        dbManager.add_user(request.email, request.password, request.name)
        return {"message": "User created successfully","data":None}
    except HTTPException as e:
        raise e

@router.post("/login")
def login(request: LoginRequest, dbManager: dbManagerDep):
    user = dbManager.get_user_by_email(request.email)
    if user==None or not pwd_context.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        access_token = create_access_token(data={"sub": user.email})
        response = JSONResponse(content={"message": "Login successful","data":{"name":user.name,"email":user.email,"access_token":access_token}})
    
       
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,  
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Time in seconds
            expires=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        # print(response.headers['cookies'])
        print(response.headers)
        return response

@router.post("/logout")
def logout():
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie("access_token")
    return response
    
@router.get("/user")
def get_user(dbManager: dbManagerDep, email: str = Depends(get_current_user)):
    print(f"Email of user islike this {email}")
    user = dbManager.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User found","data": {"name": user.name, "email": user.email}}


