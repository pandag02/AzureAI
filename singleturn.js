import 'dotenv/config';
import express from 'express';
import axios from 'axios';
import path from 'path';

//express를 통해 서버를 열 것
const app = express();
//서버 포트: 로컬
const PORT = 8080;

// EJS 설정
app.set('view engine', 'ejs');
app.set('views', path.join(process.cwd(), 'views'));
app.set('view cache', false); //view 캐시를 사용하지 않고 언제나 새로 불러옴.
app.use(express.static(path.join(process.cwd(), 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));


// FastAPI 엔드포인트
const FASTAPI_URL = "http://localhost:8000/generate-text";

// 메인 페이지 렌더링, views/index.ejs 파일을 들고오게 함.
app.get('/', (req, res) => {
  res.render('index', { responseText: null, responseData: null });  // responseData 기본값 추가
});


// FastAPI 호출 및 응답 처리
app.post('/query', async (req, res) => {
  try {
    let { text } = req.body;
    if (typeof text !== "string" || text.trim() === "") { //입력 상자를 비워두고 전송을 눌렀을 때 이 텍스트로 전송
      text = "Tell me a fun fact about technology.";
    }

    const requestData = {
      prompt: text
    };

    const response = await axios.post(FASTAPI_URL, requestData, {
      headers: { 'Content-Type': 'application/json' }
    });

    console.log("✅ FastAPI 응답 데이터:", response.data);

    if (!response.data.generated_text) {
      throw new Error("Invalid API Response: Missing 'generated_text'");
    }

    res.render('index', {
        responseText: response.data.generated_text || "응답이 없습니다.",
        responseData: response.data  // 전체 JSON 데이터를 EJS에 전달
      });
    console.log("✅ Rendering EJS file with responseText:", response.data.generated_text);
  } catch (error) {
    console.error("❌ FastAPI 호출 오류:", error);
    if (error.response) {
      console.error("❌ 오류 응답 상태 코드:", error.response.status);
      console.error("❌ 오류 응답 데이터:", error.response.data);
    }
    res.status(500).render('index', { responseText: "FastAPI 호출 실패." });
  }
});

// 서버 실행
app.listen(PORT, () => {
  console.log(`🚀 Node.js 서버 실행 중: http://localhost:${PORT}`);
});
