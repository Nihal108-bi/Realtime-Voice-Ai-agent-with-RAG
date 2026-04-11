import os
import tempfile
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from loguru import logger
from bson import ObjectId
# from app.services.text_extraction import TextExtractionService
# from app.services.embeddings import EmbeddingService

from app.database import get_database
from app.models.equipment import Equipment
from app.models.document import Document
from app.config import settings

router=APIRouter()
@router.post("/",response_model=Equipment,status_code=status.HTTP_201_CREATED)
async def create_equipment(equipment: Equipment):
    """Create a new equipment"""
    db=get_database()
    #check if equipment name already exists
    existing=await db.equipment.find_one({"name": equipment.name , "tenant_id":equipment.tenant_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Equipment with this name already exsts"
        )
    
    #Add timestamps
    now=datetime.utcnow()
    equipment_dict=equipment.model_dump(exclude={"id"},exclude_none=True)
    equipment_dict["created_at"]=now
    equipment_dict["updated_at"]=now

    #insert into database
    result=await db.equipment.insert_one(equipment_dict)
    response_dict=equipment.model_dump(exclude={"id"},exclude_none=True)
    response_dict["_id"]=str(result.inserted_id)
    return Equipment(**response_dict)

@router.get("/",response_model=List[Equipment],status_code=status.HTTP_200_OK)
async def get_equipment():
    """Get all equipment"""
    db=get_database()
    equipment_list=await db.equipment.find({}).to_list(length=None)
    result=[]
    for item in equipment_list:
        item_dict=dict(item)
        if '_id' in item_dict and isinstance(item_dict['id'],ObjectId):
            item_dict['_id']=str(item_dict['_id'])
        result.append(Equipment(**item_dict))
    return result   

@router.get("/{equipment_id}",response_model=Equipment,status_code=status.HTTP_200_OK) 
async def get_one_equipment(equipment_id: str):
    """Get an equipment by ID"""
    db=get_database()
    equipment=await db.equipment.find_one({"_id":ObjectId(equipment_id)})
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    equipment_dict=dict(equipment)
    if '_id' in equipment_dict and isinstance(equipment_dict['_id'],ObjectId):
        equipment_dict['_id']=str(equipment_dict['_id'])
    return Equipment(**equipment_dict)    