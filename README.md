# COPD Patient Assessment API
## 개요

이 프로젝트는 COPD(만성폐쇄성폐질환) 환자의 기본정보, 설문조사, 신체측정, 음성 데이터를 수집하는 FastAPI 서버입니다. 환자 평가 및 모니터링을 위한 의료 데이터 수집 API로 설계되었습니다.

## 지원 데이터 그룹

### COPD 환자 평가 데이터 (6가지)
- **Basic** (`basic`) - 기본정보 (성별, 생년월일, 키, 몸무게, 교육수준)
- **Oximeter** (`oximeter`) - 산소포화도 측정 (운동 전후 심박수, 산소포화도)
- **Chair Stand** (`chair-stand`) - 의자 일어서기 검사 (30초간 횟수)
- **Survey Voice** (`survey-voice`) - 설문조사 음성 (MBS, Borg RPE)
- **Survey** (`survey`) - 설문조사 일반 (CAT 8문항, mMRC, 흡연 관련)
- **Voice** (`voice`) - 음성 데이터 (파일 경로, 전사 텍스트, 분석 결과)


---

## 설치 및 실행

1. 레포지토리 클론  
```bash
git clone https://github.com/embed-Rayn/doctor-dairy-COPD-API.git
cd doctor-dairy-COPD-API
```
2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 환경변수 설정 (`.env` 파일)
```env
ADDRESS=0.0.0.0
PORT=8000
DATABASE_URL=postgresql://user:pass@localhost:5432/copd_assessment_db
```

4. 서버 실행
### 4-1 간단
```bash
uvicorn app.main:app --host $ADDRESS --port $PORT --reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4-2 서비스 등록(최초 1회)
로그 보기
```bash
journalctl -u copd-assessment-api -f
```
```bash
sudo vim /etc/systemd/system/copd-assessment-api.service
```
아래 등록
```
[Unit]
Description=Copd AssessmentData API (FastAPI)
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/Downloads/doctor-dairy-COPD-API
Environment="PATH=/home/ubuntu/miniconda3/envs/copd_api/bin"
ExecStart=/home/ubuntu/miniconda3/envs/copd_api/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
Restart=always

[Install]
WantedBy=multi-user.target
```
```
sudo systemctl daemon-reload
sudo systemctl restart copd-assessment-api.service
sudo systemctl status copd-assessment-api.service
```

## 프로젝트 구조
```
app/
├── main.py           # FastAPI 앱 생성, 라우터 등록
├── models.py         # 모든 Pydantic 모델 (COPD + 삼성헬스)
├── routers/          # 데이터 그룹별 라우터 (6개 파일)
│   ├── basic.py      # 기본정보
│   ├── oximeter.py   # 산소포화도
│   ├── chair_stand.py # 의자 일어서기
│   ├── survey_voice.py # 설문조사(음성)
│   ├── survey.py     # 설문조사(일반)
│   └── voice.py      # 음성 데이터
└── services/         # 공통 비즈니스 로직
    └── data_service.py
```

## API 엔드포인트

### COPD 환자 평가 API
모든 COPD 엔드포인트는 POST 메서드를 사용하며, 공통 경로는 `/app/copd/{group}` 입니다.

#### 1. 기본정보 업로드
```http
POST {{ADDRESS}}:{{PORT}}/app/copd/basic
Content-Type: application/json

{
  "USER_UUID": "PATIENT_001",
  "data": {
    "sex": 1,
    "birth": "1970-05-15",
    "height": 175.5,
    "weight": 70.2,
    "education": 4
  }
}
```

#### 2. 산소포화도 측정 업로드
```http
POST {{ADDRESS}}:{{PORT}}/app/copd/oximeter
Content-Type: application/json

{
  "USER_UUID": "PATIENT_001",
  "data": {
    "pre_HR": 72.5,
    "pre_SpO2": 98.2,
    "post_HR": 85.3,
    "post_SpO2": 96.8
  }
}
```

#### 3. 의자 일어서기 검사 업로드
```http
POST {{ADDRESS}}:{{PORT}}/app/copd/chair-stand
Content-Type: application/json

{
  "USER_UUID": "PATIENT_001",
  "data": {
    "CS_count": 15.0
  }
}
```

#### 4. 설문조사(음성) 업로드
```http
POST {{ADDRESS}}:{{PORT}}/app/copd/survey-voice
Content-Type: application/json

{
  "USER_UUID": "PATIENT_001",
  "data": {
    "MBS": 5,
    "Borg_RPE": 12
  }
}
```

#### 5. 설문조사(일반) 업로드
```http
POST {{ADDRESS}}:{{PORT}}/app/copd/survey
Content-Type: application/json

{
  "USER_UUID": "PATIENT_001",
  "data": {
    "CAT1": 2, "CAT2": 1, "CAT3": 0, "CAT4": 3,
    "CAT5": 2, "CAT6": 1, "CAT7": 0, "CAT8": 1,
    "CAT_sum": 10,
    "mMRC": 2,
    "Smoke_CAT1": 1,
    "Smoke_CAT2": 2,
    "Smoke_CAT3": 3,
    "Smoke_CAT4": 10.5
  }
}
```

#### 6. 음성 데이터 업로드 (메타데이터)
```http
POST {{ADDRESS}}:{{PORT}}/app/copd/voice
Content-Type: application/json

{
  "USER_UUID": "PATIENT_001",
  "data": {
    "voice_file_path": "/workspace/voice/sample.wav",
    "voice_file_name": "sample.wav",
    "voice_duration": 45.2,
    "voice_format": "wav",
    "voice_quality": "high",
    "transcription": "안녕하세요...",
    "analysis_result": "분석 결과..."
  }
}
```

#### 7. 음성 파일 직접 업로드
```http
POST {{ADDRESS}}:{{PORT}}/app/copd/voice/file
Content-Type: multipart/form-data

Form Data:
- file: [audio file]
- USER_UUID: PATIENT_001
- voice_quality: high (optional)
- transcription: 안녕하세요... (optional)
- analysis_result: 분석 결과... (optional)
```

## 데이터 검증 규칙

### COPD 평가 데이터 검증
- **int 타입**: 범위 제한 (예: 1~2, 0~5, 6~20)
- **float 타입**: 양수 값 (continuous)
- **String 타입**: 날짜 형식 검증 (ISO 8601)
- Pydantic Field()를 활용한 자동 검증

### 음성 파일 제한사항
- **지원 형식**: audio/* (wav, mp3, m4a 등)
- **저장 위치**: `/workspace/8889/voice_files/`
- **메타데이터**: 파일 경로, 길이, 품질, 전사 텍스트, 분석 결과

## 테스트

### 단위 테스트 실행
```bash
pytest --cov=app tests/
```

### API 테스트 (서버 실행 후)
```bash
# 기본 헬스체크
curl http://localhost:8000/

# COPD 기본정보 테스트
curl -X POST http://localhost:8000/app/copd/basic \
  -H "Content-Type: application/json" \
  -d '{
    "USER_UUID": "TEST_001",
    "data": {
      "sex": 1,
      "birth": "1970-01-01",
      "height": 170.0,
      "weight": 70.0,
      "education": 3
    }
  }'
```

## 개발 가이드

### 새로운 데이터 그룹 추가
1. `app/models.py`에 `{Group}Data`와 `{Group}Request` 모델 정의
2. `app/routers/{group}.py` 생성 (기존 패턴 참조)
3. `app/main.py`에 라우터 등록
4. 정의서.csv에 맞는 Pydantic 검증 규칙 추가

### 환경 변수
```env
ADDRESS=0.0.0.0
PORT=8000
DATABASE_URL=postgresql://user:pass@localhost:5432/copd_assessment_db
```

## 참고 자료
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Pydantic 검증 규칙](https://docs.pydantic.dev/latest/)
- [정의서.csv](./정의서.csv) - 데이터 구조 정의