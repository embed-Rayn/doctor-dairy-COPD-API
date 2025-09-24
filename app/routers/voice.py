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
    file: UploadFile = File(..., description="음성 파일"),
    USER_UUID: str = Form(..., description="환자 식별자"),
    patient_id: Optional[str] = Form(None, description="환자 ID (선택)"),
    voice_quality: Optional[str] = Form(None, description="음성 품질 (high/medium/low)"),
    transcription: Optional[str] = Form(None, description="음성 전사 텍스트"),
    analysis_result: Optional[str] = Form(None, description="음성 분석 결과")
):
    """음성 파일 직접 업로드 및 메타데이터 저장"""
    
    # 파일 크기 제한 (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="파일 크기가 너무 큽니다. (최대 50MB)")
    
    # 파일 형식 검증
    allowed_extensions = ['.wav', '.mp3', '.m4a', '.ogg', '.flac']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if not file.content_type or not file.content_type.startswith('audio/'):
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"지원하지 않는 파일 형식입니다. 허용 형식: {', '.join(allowed_extensions)}"
            )
    
    # 업로드 디렉토리 설정 (날짜별 폴더 생성)
    from datetime import datetime
    today = datetime.now().strftime("%Y%m%d")
    upload_dir = f"/workspace/8889/voice_files/{today}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 안전한 파일명 생성 (타임스탬프 + 원본명)
    import uuid
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{USER_UUID}_{timestamp}_{uuid.uuid4().hex[:8]}{file_extension}"
    file_path = os.path.join(upload_dir, safe_filename)
    
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

@router.post("/file/upload")
async def upload_general_file(
    file: UploadFile = File(..., description="업로드할 파일"),
    USER_UUID: str = Form(..., description="환자 식별자"),
    file_type: str = Form(..., description="파일 타입 (voice/image/document/other)"),
    description: Optional[str] = Form(None, description="파일 설명"),
    metadata: Optional[str] = Form(None, description="추가 메타데이터 (JSON 형식)")
):
    """범용 파일 업로드 엔드포인트"""
    
    # 파일 크기 제한
    MAX_FILE_SIZE = {
        'voice': 50 * 1024 * 1024,    # 50MB
        'image': 10 * 1024 * 1024,    # 10MB  
        'document': 20 * 1024 * 1024,  # 20MB
        'other': 100 * 1024 * 1024     # 100MB
    }
    
    size_limit = MAX_FILE_SIZE.get(file_type, MAX_FILE_SIZE['other'])
    if file.size and file.size > size_limit:
        raise HTTPException(
            status_code=413, 
            detail=f"파일 크기가 너무 큽니다. (최대 {size_limit // (1024*1024)}MB)"
        )
    
    # 파일 형식별 허용 확장자
    allowed_extensions = {
        'voice': ['.wav', '.mp3', '.m4a', '.ogg', '.flac'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'document': ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx'],
        'other': []  # 모든 형식 허용
    }
    
    if file_type != 'other':
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions[file_type]:
            raise HTTPException(
                status_code=400,
                detail=f"{file_type} 파일의 허용 형식: {', '.join(allowed_extensions[file_type])}"
            )
    
    # 디렉토리 설정
    from datetime import datetime
    today = datetime.now().strftime("%Y%m%d")
    upload_dir = f"/workspace/8889/files/{file_type}/{today}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 안전한 파일명 생성
    import uuid
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1].lower()
    safe_filename = f"{USER_UUID}_{timestamp}_{uuid.uuid4().hex[:8]}{file_extension}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    try:
        # 파일 저장
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 메타데이터 처리
        import json
        parsed_metadata = {}
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                parsed_metadata = {"raw_metadata": metadata}
        
        # 파일 정보 저장
        file_info = {
            "USER_UUID": USER_UUID,
            "original_filename": file.filename,
            "safe_filename": safe_filename,
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "file_type": file_type,
            "content_type": file.content_type,
            "description": description,
            "metadata": parsed_metadata,
            "upload_timestamp": datetime.now().isoformat()
        }
        
        # 메타데이터를 JSON으로 저장
        metadata_path = file_path + ".metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(file_info, f, ensure_ascii=False, indent=2)
        
        return {
            "message": "파일 업로드 성공",
            "file_info": file_info,
            "download_url": f"/files/{file_type}/{today}/{safe_filename}"
        }
        
    except Exception as e:
        # 에러 발생 시 파일 정리
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")
    
    finally:
        await file.close()