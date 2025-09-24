from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models import VoiceRequest
from app.services import data_service
import os
import shutil
from typing import Optional

router = APIRouter()

@router.post("/voice")
async def upload_voice_data(data: VoiceRequest):
    """음성 데이터 (파일 경로, 전사 텍스트, 분석 결과) 업로드"""
    return data_service.save_data(data)

@router.post("/voice/file")
async def upload_voice_file(
    file: UploadFile = File(...),
    USER_UUID: str = Form(...),
    voice_quality: Optional[str] = Form(None),
    transcription: Optional[str] = Form(None),
    analysis_result: Optional[str] = Form(None)
):
    """음성 파일 직접 업로드 및 메타데이터 저장"""
    
    # 파일 검증
    if not file.content_type or not file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="음성 파일만 업로드 가능합니다.")
    
    # 업로드 디렉토리 설정
    upload_dir = "/workspace/8889/voice_files"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 파일 저장
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 파일 크기로 대략적인 길이 추정 (실제로는 음성 분석 라이브러리 사용 권장)
        file_size = os.path.getsize(file_path)
        estimated_duration = file_size / 32000  # 대략적인 추정값
        
        # VoiceRequest 객체 생성
        from app.models import VoiceData
        voice_data = VoiceData(
            voice_file_path=file_path,
            voice_file_name=file.filename,
            voice_duration=estimated_duration,
            voice_format=file.content_type.split('/')[-1],
            voice_quality=voice_quality,
            transcription=transcription,
            analysis_result=analysis_result
        )
        
        voice_request = VoiceRequest(
            USER_UUID=USER_UUID,
            data=voice_data
        )
        
        # 데이터 저장
        result = data_service.save_data(voice_request)
        result["uploaded_file"] = file.filename
        result["file_path"] = file_path
        
        return result
        
    except Exception as e:
        # 에러 발생 시 파일 정리
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")
    
    finally:
        await file.close()