<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>당뇨병 예방 걷기운동 챗봇</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            width: 100%;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 90vh;
            max-height: 800px;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            text-align: center;
        }

        .header h1 {
            font-size: 24px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }

        .message {
            margin-bottom: 20px;
            display: flex;
            gap: 12px;
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            flex-direction: row-reverse;
        }

        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            flex-shrink: 0;
        }

        .user .message-avatar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .assistant .message-avatar {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        .message-content {
            max-width: 70%;
            padding: 15px 18px;
            border-radius: 18px;
            line-height: 1.6;
            word-wrap: break-word;
        }

        .user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .assistant .message-content {
            background: white;
            color: #333;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 12px;
        }

        #userInput {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 15px;
            outline: none;
            transition: all 0.3s;
        }

        #userInput:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        #sendBtn {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        #sendBtn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        #sendBtn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .loading {
            display: flex;
            gap: 5px;
            padding: 15px;
        }

        .loading span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            animation: bounce 1.4s infinite ease-in-out;
        }

        .loading span:nth-child(1) {
            animation-delay: -0.32s;
        }

        .loading span:nth-child(2) {
            animation-delay: -0.16s;
        }

        @keyframes bounce {
            0%, 80%, 100% {
                transform: scale(0);
            }
            40% {
                transform: scale(1);
            }
        }

        .suggestions {
            padding: 15px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }

        .suggestions-title {
            font-size: 13px;
            color: #666;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .suggestion-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .suggestion-chip {
            padding: 8px 16px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 20px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .suggestion-chip:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .welcome-message {
            text-align: center;
            padding: 40px 20px;
            color: #666;
        }

        .welcome-message h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 22px;
        }

        .welcome-message p {
            margin-bottom: 10px;
            line-height: 1.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚶‍♂️ 당뇨병 예방 걷기운동 챗봇</h1>
            <p>20대~40대 남성을 위한 맞춤형 걷기운동 가이드</p>
        </div>

        <div class="suggestions">
            <div class="suggestions-title">💡 추천 질문</div>
            <div class="suggestion-chips">
                <div class="suggestion-chip" onclick="sendSuggestion('하루에 몇 걸음을 걸어야 하나요?')">하루 권장 걸음 수</div>
                <div class="suggestion-chip" onclick="sendSuggestion('30대 남성의 권장 걷기시간은?')">권장 걷기시간</div>
                <div class="suggestion-chip" onclick="sendSuggestion('식후 걷기가 왜 중요한가요?')">식후 걷기 효과</div>
                <div class="suggestion-chip" onclick="sendSuggestion('효과적인 걷기 방법은?')">효과적인 걷기법</div>
            </div>
        </div>

        <div class="chat-container" id="chatContainer">
            <div class="welcome-message">
                <h2>안녕하세요! 👋</h2>
                <p>당뇨병 예방을 위한 걷기운동에 대해 궁금한 점을 물어보세요.</p>
                <p>하루 권장 걸음 수, 운동 시간, 효과적인 방법 등<br>무엇이든 물어보실 수 있습니다.</p>
            </div>
        </div>

        <div class="input-container">
            <input type="text" id="userInput" placeholder="걷기운동에 대해 궁금한 점을 물어보세요..." />
            <button id="sendBtn" onclick="sendMessage()">전송</button>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');

        // Enter 키로 전송
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !sendBtn.disabled) {
                sendMessage();
            }
        });

        function sendSuggestion(text) {
            userInput.value = text;
            sendMessage();
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            // 환영 메시지 제거
            const welcomeMsg = chatContainer.querySelector('.welcome-message');
            if (welcomeMsg) welcomeMsg.remove();

            // 사용자 메시지 추가
            addMessage(message, 'user');
            userInput.value = '';
            sendBtn.disabled = true;

            // 로딩 표시
            const loadingId = addLoading();

            // AI 응답 생성
            const response = await generateResponse(message);
            
            // 로딩 제거 및 응답 표시
            removeLoading(loadingId);
            addMessage(response, 'assistant');
            
            sendBtn.disabled = false;
            userInput.focus();
        }

        function addMessage(text, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = type === 'user' ? '👤' : '🤖';
            
            const content = document.createElement('div');
            content.className = 'message-content';
            content.textContent = text;
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(content);
            chatContainer.appendChild(messageDiv);
            
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function addLoading() {
            const loadingDiv = document.createElement('div');
            const loadingId = 'loading-' + Date.now();
            loadingDiv.id = loadingId;
            loadingDiv.className = 'message assistant';
            loadingDiv.innerHTML = `
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <div class="loading">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            chatContainer.appendChild(loadingDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return loadingId;
        }

        function removeLoading(loadingId) {
            const loadingDiv = document.getElementById(loadingId);
            if (loadingDiv) loadingDiv.remove();
        }

        async function generateResponse(userMessage) {
            // 키워드 기반 응답 생성
            const msg = userMessage.toLowerCase();
            
            if (msg.includes('걸음') || msg.includes('보수')) {
                return `20대~40대 남성의 당뇨병 예방을 위한 하루 권장 걸음 수는 약 7,000~10,000보입니다.\n\n• 최소 목표: 7,000보\n• 이상적 목표: 10,000보\n• 시간으로는 하루 30분~60분 정도입니다.\n\n꾸준히 실천하는 것이 가장 중요합니다! 처음에는 적은 걸음으로 시작해서 점차 늘려가세요.`;
            }
            
            if (msg.includes('시간') || msg.includes('30대') || msg.includes('20대') || msg.includes('40대')) {
                return `20대~40대 남성의 권장 걷기시간은 다음과 같습니다:\n\n• 하루 30분 이상, 주 5일 이상\n• 중강도 걷기: 약간 숨이 찰 정도의 속도\n• 한 번에 30분이 어렵다면 10분씩 3회로 나눠도 효과적입니다.\n\n꾸준함이 가장 중요하니, 매일 조금씩이라도 걷는 습관을 만들어보세요!`;
            }
            
            if (msg.includes('식후') || msg.includes('밥') || msg.includes('식사')) {
                return `식후 걷기는 당뇨병 예방에 매우 효과적입니다!\n\n주요 효과:\n• 식후 혈당 급상승 방지\n• 인슐린 저항성 개선\n• 소화 촉진 및 대사 활성화\n\n권장 방법:\n• 식사 후 10~15분 가벼운 걷기\n• 특히 저녁 식사 후 걷기가 효과적\n• 너무 바로 시작하지 말고 5~10분 후 시작\n\n매 끼니 후 짧게라도 걷는 습관을 들이면 당뇨병 예방에 큰 도움이 됩니다!`;
            }
            
            if (msg.includes('방법') || msg.includes('어떻게') || msg.includes('효과적')) {
                return `효과적인 걷기 운동 방법을 알려드립니다:\n\n1. 올바른 자세\n• 가슴을 펴고 시선은 전방 15m 앞\n• 팔은 자연스럽게 앞뒤로 흔들기\n• 발뒤꿈치부터 착지 후 발가락으로 밀어내기\n\n2. 적절한 강도\n• 약간 숨이 찰 정도 (대화는 가능한 수준)\n• 심박수: 최대심박수의 50~70%\n\n3. 실천 팁\n• 아침 공복 걷기 또는 식후 걷기\n• 편한 운동화 착용\n• 만보계나 스마트워치로 기록\n\n꾸준함이 가장 중요합니다!`;
            }
            
            if (msg.includes('당뇨') || msg.includes('효과') || msg.includes('예방')) {
                return `걷기운동은 당뇨병 예방에 매우 효과적입니다!\n\n주요 효과:\n• 혈당 조절 능력 향상 (인슐린 민감도 개선)\n• 체중 관리 및 내장지방 감소\n• 심혈관 건강 증진\n• 스트레스 감소\n\n연구 결과:\n• 규칙적인 걷기는 당뇨병 발병 위험을 30~40% 감소\n• 식후 걷기는 혈당 상승을 15~20% 억제\n\n20대~40대는 당뇨병 예방의 황금기입니다. 지금부터 걷기 습관을 만들면 평생 건강을 지킬 수 있습니다!`;
            }

            // 기본 응답
            return `안녕하세요! 당뇨병 예방을 위한 걷기운동에 대해 궁금하신 점이 있으시군요.\n\n20대~40대 남성을 위한 기본 권장사항:\n• 하루 7,000~10,000보 걷기\n• 하루 30분 이상, 주 5일 이상\n• 식후 10~15분 걷기로 혈당 관리\n• 중강도 걷기 (약간 숨이 찰 정도)\n\n더 구체적인 질문이 있으시면 언제든지 물어보세요!\n예: "하루 권장 걸음 수는?", "식후 걷기 효과는?", "효과적인 걷기 방법은?" 등`;
        }
    </script>
</body>
</html>
