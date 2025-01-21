require('dotenv').config(); // ✅ 환경 변수 불러오기

const express = require('express');
const axios = require('axios');
const cors = require('cors');  
const path = require('path'); 

const app = express(); // ✅ 먼저 선언해야 함
const PORT = 8080;

// ✅ EJS 설정은 app 선언 후에 해야 함
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(cors()); // CORS 허용
app.use(express.json()); // JSON 요청 처리
app.use(express.urlencoded({ extended: true })); // 폼 데이터 받기
app.use(express.static(path.join(__dirname, 'public')));

// ✅ 환경 변수에서 API 정보 가져오기
const AZURE_AI_ENDPOINT = process.env.AZURE_AI_ENDPOINT;
const AZURE_API_KEY = process.env.AZURE_API_KEY;

// ✅ 기본 페이지 렌더링 (EJS 사용)
app.get('/', (req, res) => {
  res.render('index', { responseText: null });
});

// ✅ Azure AI에 데이터 보내고 결과 받기
app.post('/query', async (req, res) => {
    try {
        const userInput = req.body.text;

        const response = await axios.post(AZURE_AI_ENDPOINT, {
            prompt: userInput,
            max_tokens: 100
        }, {
            headers: {
                'Authorization': `Bearer ${AZURE_API_KEY}`,
                'Content-Type': 'application/json'
            }
        });

        const aiResponse = response.data.choices[0].text.trim();
        res.render('index', { responseText: aiResponse }); // ✅ 응답을 EJS에 전달
    } catch (error) {
        console.error('Azure AI API 호출 오류:', error);
        res.status(500).send('Azure AI API 호출 실패');
    }
});

// ✅ 서버 실행
app.listen(PORT, () => {
  console.log(`서버 실행 중: http://localhost:${PORT}`);
});
