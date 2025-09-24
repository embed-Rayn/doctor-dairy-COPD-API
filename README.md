# samsung-health-data-api
## 개요

이 프로젝트는 환자 웨어러블(삼성헬스)에서 수집된 7가지 주요 바이탈 데이터를 FastAPI 서버로 전송·저장하기 위한 API를 제공합니다.  

지원 데이터 종류:
- Skin Temperature (`ST`)
- Blood Pressure (`BP`)
- Blood Glucose (`BG`)
- Blood Oxygen (`BO`)
- Heart Rate (`HR`)
- Sleep Session (`SS`)
- Step Daily (`SD`) :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}

Postman 컬렉션(`SamsungHealthData_20250417.postman_collection.json`)을 참고하여 각 엔드포인트를 테스트할 수 있습니다. :contentReference[oaicite:2]{index=2}&#8203;:contentReference[oaicite:3]{index=3}

---

## 설치 및 실행

1. 레포지토리 클론  
```bash
git clone https://your.git.repo/fastapi_samsung_health.git
cd fastapi_samsung_health
```
2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 환경변수 설정 (`.env` 파일)
```env
ADDRESS=0.0.0.0
PORT=8000
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
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
journalctl -u health-api -f
```
```bash
sudo vim /etc/systemd/system/health-api.service
```
아래 등록
```
[Unit]
Description=Samsung Health Data API (FastAPI)
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/Downloads/samsung-health-data-api
Environment="PATH=/home/ubuntu/miniconda3/envs/fastapi/bin"
ExecStart=/home/ubuntu/miniconda3/envs/fastapi/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
Restart=always

[Install]
WantedBy=multi-user.target
```
```
sudo systemctl daemon-reload
sudo systemctl restart health-api.service
sudo systemctl status health-api.service
```
## 디렉토리 설명
- app/main.py
    - 애플리케이션 생성 및 라우터 등록
- app/models.py
    - 모든 DATA_LIST 항목에 대한 Pydantic 모델
- app/routers/
    - 각 데이터 타입별로 @router.post("/app/smc_uploaddata/{type}") 엔드포인트 정의
- app/services/data_service.py
    - 공통 저장·검증 기능 분리
- tests/
    - pytest 기반 단위 테스트

## 엔드포인트
모든 엔드포인트는 POST 메서드를 사용하며, 공통 경로는 `/app/smc_uploaddata/<type>` 입니다.

예시 (Skin Temperature):

```http
POST {{ADDRESS}}:{{PORT}}/app/smc_uploaddata/st
Content-Type: application/json

{
  "USER_UUID": "AXXXXXXXXXXXXXXXX",
  "DATA_TYPE": "ST",
  "DATA_LIST": [
    {
      "DATA_UUID": "ST1XXXXXXXXXXXXXXX",
      "START_TIME": 16344301858000,
      "END_TIME": 16344311858000,
      "TIME_OFFSET": 3600000,
      "TEMPERATURE": 36.5,
      "MIN": 36.0,
      "MAX": 37.0
    },
    …
  ]
}

```
Other endpoints:
- /app/smc_uploaddata/bp (Blood Pressure)
- /app/smc_uploaddata/bg (Blood Glucose)
- /app/smc_uploaddata/bo (Blood Oxygen)
- /app/smc_uploaddata/hr (Heart Rate)
- /app/smc_uploaddata/ss (Sleep Session)
- /app/smc_uploaddata/sd (Step Daily) ​

## TEST
```bash
pytest --cov=app tests/
```