from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from database.connection import get_session
from models.channels import Channel

router = APIRouter()


@router.get("/", response_model=List[Channel])
async def retrieve_all_Channels(session=Depends(get_session)):
    query = select(Channel)
    channels = session.exec(query).all()
    return channels
