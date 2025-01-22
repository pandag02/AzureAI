##############################################################
'''
서버, fastapi 사용하지 않고 그냥 호출해본 기본 파이썬 코드. 실행할 때마다 토큰 나가니 주의.
'''

import requests
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
API_KEY = os.getenv("AZURE_API_KEY")
ENDPOINT = os.getenv("AZURE_AI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
API_VERSION = os.getenv("AZURE_API_VERSION")
URL=os.getenv("Model_ENDPOINT")

# 텍스트 생성 함수
def generate_text(prompt):
    # API URL 구성
    url = URL
    
    # 요청 헤더
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }

    # 요청 데이터
    data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }

    # API 호출
    response = requests.post(url, headers=headers, json=data)

    # 결과 처리
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

# 테스트 실행
if __name__ == "__main__":
    try:
        user_prompt = "Where is capital of korea?"
        result = generate_text(user_prompt)
        print("Generated Text:", result)
    except Exception as e:
        print("Error occurred:", e)
