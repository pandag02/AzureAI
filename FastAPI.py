##############################################################
'''
fastapi 사용해서 api 호출.
명령어: uvicorn FastAPI:app --reload
'''
##############################################################

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
# 클라이언트가 보내는 데이터를 검증하고 관리
class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 70
    temperature: float = 0.7

# /generate-text 엔드포인트 정의
# 클라이언트에서 이 엔드포인트로 POST 요청을 보낼 수 있음
@app.post("/generate-text") 
async def generate_text(request: PromptRequest):
    # Azure OpenAI API 호출 URL
    url = URL

    # 요청 헤더 및 데이터 구성
    headers = {
        "Content-Type": "application/json", # 요청 본문 형식식
        "api-key": API_KEY
    }
    data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": request.prompt} # 사용자가 입력한 프롬프트트
        ],
        "max_tokens": request.max_tokens, # 최대 토큰 수
        "temperature": request.temperature # 창의성 수준
    }

    # Azure OpenAI API 호출
    try:
        # POST 요청으로 데이터 전송
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # HTTP 오류 발생하면 예외 발생
        result = response.json() # 음답 데이터 -> JSON 형식으로 변환환
        return {
            "generated_text": result["choices"][0]["message"]["content"], # 생성된 텍스트트
            "usage": result.get("usage", {}) 
        }

    # 요청 실패 에러 처리
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Azure OpenAI API 호출 실패: {str(e)}")
