from typing import TYPE_CHECKING, List
from sqlmodel import Column, Field, Relationship, SQLModel, String
from passlib.context import CryptContext

if TYPE_CHECKING:
    from .project import Project  

class User(SQLModel, table=True):
    email:str = Field(String, primary_key=True, index=True)
    password_hash:str 
    name:str 
    
    projects: List["Project"] = Relationship(back_populates="user")
    
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")