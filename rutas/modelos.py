from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from typing import Optional


router = APIRouter()



@router.post("/datos")
def recibir_datos():
    
    return {"message": "ok"}