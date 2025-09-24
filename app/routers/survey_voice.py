from fastapi import APIRouter
from app.models import SurveyVoiceRequest
from app.services import data_service

router = APIRouter()

@router.post("/survey-voice")
async def upload_survey_voice_data(data: SurveyVoiceRequest):
    """설문조사 음성 (MBS, Borg RPE) 업로드"""
    return data_service.save_data(data)