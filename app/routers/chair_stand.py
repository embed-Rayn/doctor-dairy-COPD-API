from fastapi import APIRouter
from app.models import ChairStandRequest
from app.services import data_service

router = APIRouter()

@router.post("/chair-stand")
async def upload_chair_stand_data(data: ChairStandRequest):
    """의자 일어서기 검사 (30초간 횟수) 업로드"""
    return data_service.save_data(data)