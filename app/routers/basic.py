from fastapi import APIRouter
from app.models import BasicInfoRequest
from app.services import data_service

router = APIRouter()

@router.post("/basic")
async def upload_basic_info(data: BasicInfoRequest):
    """기본정보 (성별, 생년월일, 키, 몸무게, 교육수준) 업로드"""
    return data_service.save_data(data)