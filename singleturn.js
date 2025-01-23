import 'dotenv/config';
import express from 'express';
import axios from 'axios';
import path from 'path';
import { MongoClient } from 'mongodb';

// Express 서버 설정
const app = express();
const PORT = 8080;

// MongoDB 연결 설정 (환경 변수에서 불러오기)
const url = process.env.MONGO_URI;
if (!url) {
  console.error("❌ 환경 변수 `MONGO_URI`가 설정되지 않았습니다. `.env` 파일을 확인하세요.");
  process.exit(1); // 환경 변수가 없으면 서버 종료
}

let db;

// MongoDB 연결
new MongoClient(url).connect()
  .then((client) => {
    console.log('✅ MongoDB 연결 성공');
    db = client.db('Testing'); // 데이터베이스 이름
  })
  .catch((err) => {
    console.error("❌ MongoDB 연결 실패:", err);
    process.exit(1); // 연결 실패 시 서버 종료
  });

// EJS 설정
app.set('view engine', 'ejs');
app.set('views', path.join(process.cwd(), 'views'));
app.set('view cache', false); // 캐싱 비활성화
app.use(express.static(path.join(process.cwd(), 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// FastAPI 엔드포인트
const FASTAPI_URL = "http://localhost:8000/generate-text";

// 메인 페이지 렌더링
app.get('/', (req, res) => {
  res.render('index', { responseText: null, responseData: null });
});

// FastAPI 호출 및 응답 저장
app.post('/query', async (req, res) => {
  try {
    let { text } = req.body;
    if (!text || typeof text !== "string" || text.trim() === "") {
      text = "Tell me a fun fact about technology.";
    }

    // FastAPI에 요청 보낼 데이터
    const requestData = { prompt: text };

    // FastAPI 호출
    const response = await axios.post(FASTAPI_URL, requestData, {
      headers: { 'Content-Type': 'application/json' }
    });

    console.log("✅ FastAPI 응답 데이터:", response.data);

    if (!response.data.generated_text) {
      throw new Error("Invalid API Response: Missing 'generated_text'");
    }

    // MongoDB에 저장
    await db.collection('post').insertOne({
      prompt: text,
      generated_text: response.data.generated_text,
      timestamp: new Date()
    });

    res.render('index', {
      responseText: response.data.generated_text || "응답이 없습니다.",
      responseData: response.data
    });

    console.log("✅ MongoDB 저장 완료:", { prompt: text, generated_text: response.data.generated_text });
  } catch (error) {
    console.error("❌ FastAPI 호출 오류:", error);
    if (error.response) {
      console.error("❌ 오류 응답 상태 코드:", error.response.status);
      console.error("❌ 오류 응답 데이터:", error.response.data);
    }
    res.status(500).render('index', { responseText: "FastAPI 호출 실패.", responseData: null });
  }
});

// 저장된 데이터 목록 조회
app.get('/list', async (req, res) => {
  try {
    const results = await db.collection('post').find().toArray();
    res.json(results); // JSON 형태로 반환
  } catch (error) {
    console.error("❌ 데이터 조회 오류:", error);
    res.status(500).json({ error: "데이터 조회 실패" });
  }
});

// 서버 실행
app.listen(PORT, () => {
  console.log(`🚀 Node.js 서버 실행 중: http://localhost:${PORT}`);
});
