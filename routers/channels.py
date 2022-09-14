from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from database.connection import get_session
from models.channels import Channels

router = APIRouter()


@router.get("/", response_model=List[Channels])
async def retrieve_all_Channels(session=Depends(get_session)):
    """
    Get all channels
    """
    query = select(Channels)
    channels = session.exec(query).all()
    return channels
