from fastapi import APIRouter
from app.models import SurveyRequest
from app.services import data_service

router = APIRouter()

@router.post("/survey")
async def upload_survey_data(data: SurveyRequest):
    """설문조사 (CAT 8문항, mMRC, 흡연 관련) 업로드"""
    return data_service.save_data(data)