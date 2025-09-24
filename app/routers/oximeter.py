from fastapi import APIRouter
from app.models import OximeterRequest
from app.services import data_service

router = APIRouter()

@router.post("/oximeter")
async def upload_oximeter_data(data: OximeterRequest):
    """산소포화도 측정 (운동 전후 심박수, 산소포화도) 업로드"""
    return data_service.save_data(data)