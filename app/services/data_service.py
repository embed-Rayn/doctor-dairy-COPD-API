import json
import os
from datetime import datetime

def save_data(data):
    # 저장 디렉토리 생성
    save_dir = "/workspace/8889/data"
    os.makedirs(save_dir, exist_ok=True)

    # 파일명: 데이터 타입_타임스탬프.json
    data_type = getattr(data, "DATA_TYPE", "unknown")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f") 
    filename = f"{data_type}_{timestamp}.json"
    filepath = os.path.join(save_dir, filename)

    # Pydantic 모델을 dict로 변환 후 저장
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data.dict(), f, ensure_ascii=False, indent=2)

    return {"result": "success", "filepath": filepath}