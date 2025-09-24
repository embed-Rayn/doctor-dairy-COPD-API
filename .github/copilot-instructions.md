# GitHub Copilot Instructions for COPD Patient Assessment API

## 프로젝트 개요
이 프로젝트는 COPD(만성폐쇄성폐질환) 환자의 기본정보, 설문조사, 신체측정 데이터를 수집하는 FastAPI 서버입니다. 환자 평가 및 모니터링을 위한 의료 데이터 수집 API로 설계되었습니다.

## 핵심 아키텍처 패턴

### 1. 데이터 그룹별 모듈 분리
- **5가지 데이터 그룹**: Basic(기본정보), Oximeter(산소포화도), Chair Stand(의자 일어서기), Survey(설문조사), Voice(음성 데이터)
- 각 그룹은 개별 라우터 + 공통 서비스 + 전용 Pydantic 모델로 구현
- 예시: `app/routers/basic.py` → `BasicInfoRequest` 모델 → `assessment_service.save_data()`

### 2. 정의서 기반 데이터 구조
정의서.csv를 기반으로 한 데이터 타입 및 검증 규칙:
```python
# 기본정보 (Basic)
{
    "sex": 1,  # int, 1~2 (1:남성, 2:여성)
    "birth": "1990-01-01",  # String, 생년월일
    "height": 170.5,  # float, 키(cm)
    "weight": 65.2,  # float, 몸무게(kg)
    "education": 3  # int, 1~6 (교육수준)
}

# 산소포화도 측정 (Oximeter)
{
    "pre_HR": 72.5,  # float, 운동 전 심박수
    "pre_SpO2": 98.2,  # float, 운동 전 산소포화도
    "post_HR": 85.3,  # float, 운동 후 심박수  
    "post_SpO2": 96.8  # float, 운동 후 산소포화도
}

# 의자 일어서기 검사 (Chair Stand)
{
    "CS_count": 15.0  # float, 30초간 의자 일어서기 횟수
}

# 설문조사 (SurveyVoice)
{
    "MBS": 5,  # int, 0~10 (Modified Borg Scale)
    "Borg_RPE": 12,  # int, 6~20 (Rate of Perceived Exertion)
}
# 설문조사 (Survey)
{
    "CAT1": 2, "CAT2": 1, "CAT3": 0, "CAT4": 3,  # int, 0~5 각각
    "CAT5": 2, "CAT6": 1, "CAT7": 0, "CAT8": 1,  # CAT 설문 8문항
    "CAT_sum": 10,  # int, 0~40 (CAT 총합)
    "mMRC": 2,  # int, 0~4 (Modified Medical Research Council)
    "Smoke_CAT1": 1,  # int, 1~2 (흡연 유무)
    "Smoke_CAT2": 2,  # int, 1~2 (금연 여부)
    "Smoke_CAT3": 3,  # int, 1~3 (금연 기간)
    "Smoke_CAT4": 10.5  # float, continuous (흡연량)
}

# 음성 데이터 (Voice) - 메타데이터만
{
    "voice_file_path": "./data/voice_files/20240924/sample.wav",  # str, 음성 파일 경로
    "transcription": "안녕하세요..."  # Optional[str], 음성 전사 텍스트
}

# 음성 파일 직접 업로드 (multipart/form-data)
curl -X POST "/app/copd/voice/file" \
     -F "file=@./audio.wav" \
     -F "USER_UUID=patient-001" \
     -F "transcription=안녕하세요"
```

### 3. 엔드포인트 네이밍 규칙
- **모든 POST 엔드포인트**: `/app/copd/{group}`
- **그룹 매핑**: basic, oximeter, chair-stand, survey-voice, survey, voice
- **특별 엔드포인트**: `/app/copd/voice/file` (음성 파일 직접 업로드)
- 공통 요청 헤더: `USER_UUID` (호환성 유지)

## 개발 가이드라인

### 새로운 데이터 그룹 추가
1. `app/models.py`에 `{Group}Data`와 `{Group}Request` 모델 정의
2. `app/routers/{group}.py` 생성 (기존 라우터와 동일한 패턴)
3. `app/main.py`에 라우터 등록
4. 정의서.csv에 맞는 Pydantic 검증 규칙 추가

### 데이터 검증 규칙 (정의서 기반)
- **int 타입**: 범위 제한 (예: 1~2, 0~5, 6~20)
- **float 타입**: continuous (연속값)
- **String 타입**: 날짜 형식 검증
- Pydantic Field() 활용하여 min/max 값 검증

### 데이터베이스 스키마 규칙
- 모든 테이블은 `patient_id`, `assessment_date` 복합 UNIQUE 제약조건 사용
- 날짜 필드는 DATE 타입 또는 TIMESTAMP
- `created_at`, `updated_at` 필드는 자동 생성
- 테이블명은 snake_case 사용: `patient_basic`, `oximeter_data`, `chair_stand_test`, `survey_data`

### 서비스 레이어 패턴
- `app/services/data_service.py`는 모든 데이터 그룹에 공통으로 사용
- 현재는 JSON 파일 저장 구현 (`./data/` 디렉토리), 향후 PostgreSQL 연동 예정
- 음성 파일은 `./data/voice_files/YYYYMMDD/` 디렉토리에 날짜별로 저장
- 파일명 규칙: `{USER_UUID}_{timestamp}_{randomid}.{extension}`
- 새로운 비즈니스 로직은 서비스 레이어에 추가

### 개발 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행 (핫 리로드)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 테스트 실행
pytest --cov=app tests/
```

### 환경 변수 (.env)
```env
ADDRESS=0.0.0.0
PORT=8000
DATABASE_URL=postgresql://user:pass@localhost:5432/copd_assessment_db
```

## 주요 제약사항

### Pydantic 모델 규칙
- 날짜 필드는 `str` 타입 (ISO 8601 형식)
- 측정값은 `float` 타입 (정밀도 고려)
- 설문 응답은 `int` 타입, 범위 검증 필수
- 모든 필드는 필수값 (Optional 사용 최소화)

### 파일 구조 유지
```
app/
├── main.py           # FastAPI 앱 생성, 라우터 등록
├── models.py         # 모든 Pydantic 모델 (단일 파일)
├── routers/          # 데이터 그룹별 라우터 (6개 파일)
│   ├── basic.py      # 기본정보
│   ├── oximeter.py   # 산소포화도
│   ├── chair_stand.py # 의자 일어서기
│   ├── survey_voice.py # 설문조사(음성)
│   ├── survey.py     # 설문조사(일반)
│   └── voice.py      # 음성 데이터
└── services/         # 공통 비즈니스 로직
```

### 에러 처리 패턴
- Pydantic 자동 검증 활용
- HTTP 상태 코드 표준 준수
- 에러 응답 형식 일관성 유지

## 테스트 및 배포

### API 테스트
정의서.csv의 데이터 타입과 범위에 맞는 테스트 케이스 작성 필요

**음성 파일 업로드 테스트 예제:**
```bash
# Windows PowerShell에서
curl.exe -X POST "http://localhost:8000/app/copd/voice/file" \
         -F "file=@./audio_sample.wav" \
         -F "USER_UUID=patient-001" \
         -F "transcription=테스트 음성입니다"

# Linux/macOS에서
curl -X POST "http://localhost:8000/app/copd/voice/file" \
     -F "file=@./audio_sample.wav" \
     -F "USER_UUID=patient-001" \
     -F "transcription=테스트 음성입니다"
```

### 운영 배포 (systemd)
```bash
# 서비스 등록
sudo systemctl daemon-reload
sudo systemctl restart copd-assessment-api.service
sudo systemctl status copd-assessment-api.service

# 로그 확인
journalctl -u copd-assessment-api -f
```

### 성능 고려사항
- 환자별 평가 데이터 처리
- 동시 접속 처리를 위한 비동기 패턴 사용
- 데이터베이스 연결 풀링 고려 필요 (향후)