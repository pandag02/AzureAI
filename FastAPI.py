##############################################
'''
- history를 반영할 수 있는 멀티턴 예제
- 단독 사용 시 history 반영 x
- history를 저장하고 처리하는 서버 및및 데이터베이스 필요
- 실행 명령어: uvicorn FastAPI:app --reload
'''
##############################################

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AZURE_API_KEY")
ENDPOINT = os.getenv("AZURE_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
API_VERSION = os.getenv("AZURE_API_VERSION")
URL = os.getenv("Model_ENDPOINT")

app = FastAPI()

# 요청 모델
class PromptRequest(BaseModel):
    prompt: str
    history: list = []  # 이전 대화 기록 포함
    max_tokens: int = 100
    temperature: float = 0.7

@app.post("/generate-text")
async def generate_text(request: PromptRequest):
    # 대화 기록과 새로운 프롬프트 병합
    messages = request.history + [{"role": "user", "content": request.prompt}]

    headers = {"Content-Type": "application/json", "api-key": API_KEY}
    data = {
        "messages": messages,
        "max_tokens": request.max_tokens,
        "temperature": request.temperature
    }

    try:
        response = requests.post(URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return {
            "generated_text": result["choices"][0]["message"]["content"],
            "usage": result.get("usage", {}),
            "history": messages + [{"role": "assistant", "content": result["choices"][0]["message"]["content"]}
            ]  # 업데이트된 대화 기록 반환
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Azure OpenAI API 호출 실패: {str(e)}")