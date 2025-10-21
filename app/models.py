from pydantic import BaseModel, Field
from typing import List, Optional

# COPD 환자 평가 데이터 모델 (정의서.csv 기반)

# 기본정보 그룹
class BasicInfoData(BaseModel):
    sex: int = Field(..., ge=1, le=2, description="성별: 1=남성, 2=여성")
    birth: str = Field(..., description="생년월일 (YYYY-MM-DD)")
    height: float = Field(..., gt=0, description="키 (cm)")
    weight: float = Field(..., gt=0, description="몸무게 (kg)")
    education: int = Field(..., ge=1, le=6, description="교육수준: 1~6")

class BasicInfoRequest(BaseModel):
    USER_UUID: str = Field(..., description="환자 식별자 (호환성)")
    data: BasicInfoData

# 산소포화도 측정 그룹
class OximeterData(BaseModel):
    pre_HR: float = Field(..., description="운동 전 심박수")
    pre_SpO2: float = Field(..., description="운동 전 산소포화도")
    post_HR: float = Field(..., description="운동 후 심박수")
    post_SpO2: float = Field(..., description="운동 후 산소포화도")

class OximeterRequest(BaseModel):
    USER_UUID: str = Field(..., description="환자 식별자 (호환성)")
    data: OximeterData

# 의자 일어서기 검사 그룹
class ChairStandData(BaseModel):
    CS_count: float = Field(..., ge=0, description="30초간 의자 일어서기 횟수")

class ChairStandRequest(BaseModel):
    USER_UUID: str = Field(..., description="환자 식별자 (호환성)")
    data: ChairStandData

# 개별 음성 파일 데이터 (파일 업로드용)
class SingleVoiceFile(BaseModel):
    voice_file_path: str = Field(..., description="음성 파일 경로")
    transcription: Optional[str] = Field(None, description="음성 전사 텍스트")

# 설문조사 + 음성 데이터 통합 그룹
class SurveyVoiceData(BaseModel):
    # 설문조사 데이터
    MBS: int = Field(..., ge=0, le=10, description="Modified Borg Scale: 0~10")
    Borg_RPE: int = Field(..., ge=6, le=20, description="Rate of Perceived Exertion: 6~20")
    
    # 4개의 음성 데이터
    voice_pre_ah: SingleVoiceFile = Field(..., description="Chair Standing 전 '아~' 소리")
    voice_post_ah: SingleVoiceFile = Field(..., description="Chair Standing 후 '아~' 소리")
    voice_pre_paragraph: SingleVoiceFile = Field(..., description="문단 읽기 1")
    voice_post_paragraph: SingleVoiceFile = Field(..., description="문단 읽기 2")

class SurveyVoiceRequest(BaseModel):
    USER_UUID: str = Field(..., description="환자 식별자 (호환성)")
    data: SurveyVoiceData

# 설문조사 그룹
class SurveyData(BaseModel):
    CAT1: int = Field(..., ge=0, le=5, description="CAT 설문 1번: 0~5")
    CAT2: int = Field(..., ge=0, le=5, description="CAT 설문 2번: 0~5")
    CAT3: int = Field(..., ge=0, le=5, description="CAT 설문 3번: 0~5")
    CAT4: int = Field(..., ge=0, le=5, description="CAT 설문 4번: 0~5")
    CAT5: int = Field(..., ge=0, le=5, description="CAT 설문 5번: 0~5")
    CAT6: int = Field(..., ge=0, le=5, description="CAT 설문 6번: 0~5")
    CAT7: int = Field(..., ge=0, le=5, description="CAT 설문 7번: 0~5")
    CAT8: int = Field(..., ge=0, le=5, description="CAT 설문 8번: 0~5")
    CAT_sum: int = Field(..., ge=0, le=40, description="CAT 총합: 0~40")
    mMRC: int = Field(..., ge=0, le=4, description="Modified Medical Research Council: 0~4")
    Smoke_CAT1: int = Field(..., ge=1, le=2, description="흡연 유무: 1~2")
    Smoke_CAT2: int = Field(..., ge=1, le=3, description="금연 여부: 1~3")
    Smoke_CAT3: int = Field(..., ge=1, le=4, description="금연 기간: 1~4")
    Smoke_CAT4: float = Field(..., ge=0, description="흡연량 (연속값)")

class SurveyRequest(BaseModel):
    USER_UUID: str = Field(..., description="환자 식별자 (호환성)")
    data: SurveyData

# 음성 파일 메타데이터 (기존 호환성 유지용 - Deprecated)
class VoiceData(BaseModel):
    voice_file_path: str = Field(..., description="음성 파일 경로")
    transcription: Optional[str] = Field(None, description="음성 전사 텍스트")

class VoiceRequest(BaseModel):
    USER_UUID: str = Field(..., description="환자 식별자 (호환성)")
    data: VoiceData