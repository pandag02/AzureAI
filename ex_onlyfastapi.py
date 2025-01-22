
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
API_KEY = os.getenv("AZURE_API_KEY")
ENDPOINT = os.getenv("AZURE_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
API_VERSION = os.getenv("AZURE_API_VERSION")
URL=os.getenv("Model_ENDPOINT")

# FastAPI 인스턴스 생성
app = FastAPI()

# 요청 바디 모델 정의
class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7

# 엔드포인트 정의
@app.post("/generate-text")
async def generate_text(request: PromptRequest):
    # Azure OpenAI API 호출 URL 생성
    url = URL

    # 요청 헤더 및 데이터 구성
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": request.prompt}
        ],
        "max_tokens": request.max_tokens,
        "temperature": request.temperature
    }

    # API 호출
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        result = response.json()
        return {
            "generated_text": result["choices"][0]["message"]["content"],
            "usage": result.get("usage", {})
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Azure OpenAI API 호출 실패: {str(e)}")

