# COPD Patient Assessment API
## 개요

이 프로젝트는 COPD(만성폐쇄성폐질환) 환자의 기본정보, 설문조사, 신체측정, 음성 데이터를 수집하는 FastAPI 서버입니다. 환자 평가 및 모니터링을 위한 의료 데이터 수집 API로 설계되었습니다.

## 지원 데이터 그룹

### COPD 환자 평가 데이터 (6가지)
- **Basic** (`basic`) - 기본정보 (성별, 생년월일, 키, 몸무게, 교육수준)
- **Oximeter** (`oximeter`) - 산소포화도 측정 (운동 전후 심박수, 산소포화도)
- **Chair Stand** (`chair-stand`) - 의자 일어서기 검사 (30초간 횟수)
- **Survey Voice** (`survey-voice`) - 설문조사 + 음성 데이터 (MBS, Borg RPE + 4개의 음성 파일)
  - Chair Standing 전/후 "아~" 소리 2개
  - Chair Standing 전/후  문단 읽기 음성 2개
- **Survey** (`survey`) - 설문조사 일반 (CAT 8문항, mMRC, 흡연 관련)
- **Voice** (`voice`) - 개별 음성 파일 업로드 (기존 호환성 유지용)


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
  "USER_UUID": "SS0001",
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
  "USER_UUID": "SS0001",
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
  "USER_UUID": "SS0001",
  "data": {
    "CS_count": 15.0
  }
}
```

#### 4. 설문조사(음성) + 4개 음성 파일 업로드
```http
POST {{ADDRESS}}:{{PORT}}/app/copd/survey-voice
Content-Type: multipart/form-data

Form Data:
- USER_UUID: SS0001
- MBS: 5
- Borg_RPE: 12
- voice_pre_ah: [audio file] - Chair Standing 전 "아~" 소리
- voice_post_ah: [audio file] - Chair Standing 후 "아~" 소리
- voice_pre_paragraph: [audio file] - Chair Standing 전 문단 읽기
- voice_post_paragraph: [audio file] - Chair Standing 후 문단 읽기 
- transcription_pre_ah: "아~" (optional)
- transcription_post_ah: "아~" (optional)
- transcription_pre_paragraph: "문단 내용..." (optional)
- transcription_post_paragraph: "문단 내용..." (optional)
```

**curl 예제:**
```bash
curl -X POST "http://localhost:8000/app/copd/survey-voice" \
     -F "USER_UUID=SS00001" \
     -F "MBS=5" \
     -F "Borg_RPE=12" \
     -F "voice_pre_ah=@./pre_ah.wav" \
     -F "voice_post_ah=@./post_ah.wav" \
     -F "voice_pre_paragraph=@./paragraph_1.wav" \
     -F "voice_post_paragraph=@./paragraph_2.wav" \
     -F "transcription_pre_ah=아~" \
     -F "transcription_post_ah=아~" \
     -F "transcription_pre_paragraph=첫 번째 문단 내용입니다" \
     -F "transcription_post_paragraph=두 번째 문단 내용입니다"
```

**저장 위치:**
- 파일: `./data/voice_files/YYYYMMDD/USER_UUID_{file_type}_timestamp_randomid.wav`
- 파일 타입: `pre_ah`, `post_ah`, `paragraph_1`, `paragraph_2`
- 메타데이터: JSON 형식으로 설문 데이터와 함께 저장

#### 5. 설문조사(일반) 업로드
```http
POST {{ADDRESS}}:{{PORT}}/app/copd/survey
Content-Type: application/json

{
  "USER_UUID": "SS0001",
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

#### 6. 개별 음성 파일 업로드 (기존 호환성 유지용)
```http
POST {{ADDRESS}}:{{PORT}}/app/copd/voice
Content-Type: application/json

{
  "USER_UUID": "SS0001",
  "data": {
    "voice_file_path": "/workspace/voice/sample.wav",
    "transcription": "안녕하세요..."
  }
}
```

#### 7. 개별 음성 파일 직접 업로드 (기존 호환성 유지용)
```http
POST {{ADDRESS}}:{{PORT}}/app/copd/voice/file
Content-Type: multipart/form-data

Form Data:
- file: [audio file]
- USER_UUID: SS0001
- transcription: 안녕하세요... (optional)
```

**curl 예제:**
```bash
# 필수 파라미터만 사용
curl -X POST "http://localhost:8000/app/copd/voice/file" \
     -F "file=@./audio_sample.wav" \
     -F "USER_UUID=SS00001"

# 전사 텍스트 포함
curl -X POST "http://localhost:8000/app/copd/voice/file" \
     -F "file=@./audio_sample.wav" \
     -F "USER_UUID=SS00001" \
     -F "transcription=안녕하세요, 테스트입니다"
```

**저장 위치:**
- 파일: `./data/voice_files/YYYYMMDD/USER_UUID_timestamp_randomid.wav`
- 메타데이터: `./data/unknown_timestamp.json`

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

# 설문조사 + 음성 파일 업로드 테스트 (주요 엔드포인트)
curl -X POST http://localhost:8000/app/copd/survey-voice \
  -F "USER_UUID=TEST_001" \
  -F "MBS=5" \
  -F "Borg_RPE=12" \
  -F "voice_pre_ah=@./test_pre_ah.wav" \
  -F "voice_post_ah=@./test_post_ah.wav" \
  -F "voice_pre_paragraph=@./test_pre_paragraph.wav" \
  -F "voice_post_paragraph=@./test_post_paragraph.wav" \
  -F "transcription_pre_ah=아~" \
  -F "transcription_post_ah=아~"

# 개별 음성 파일 업로드 테스트 (기존 호환성)
curl -X POST http://localhost:8000/app/copd/voice/file \
  -F "file=@./test_audio.wav" \
  -F "USER_UUID=TEST_001" \
  -F "transcription=테스트 음성입니다"
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