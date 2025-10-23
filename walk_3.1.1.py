import streamlit as st
from openai import OpenAI
import json

# 🔹 Streamlit 기본 설정
st.set_page_config(page_title="당뇨병 예방 걷기운동 챗봇", page_icon="🚶‍♂️", layout="centered")

# 🔹 OpenAI API 키 설정 (환경변수 사용 권장)
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY"))

# 🔹 JavaScript에서 Streamlit으로 메시지를 전달할 때 사용할 Streamlit 함수
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ✅ GPT 답변 생성 함수
def get_gpt_response(user_message: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 당뇨병 예방과 걷기운동에 대해 잘 아는 친절한 건강 코치야. 사용자의 질문에 정확하고 따뜻하게 답해줘."},
                {"role": "user", "content": user_message}
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ 오류가 발생했어요: {str(e)}"

# 🔹 JS → Python 호출용 Streamlit API endpoint
import streamlit.components.v1 as components

# ✅ HTML + JS (기존 디자인 유지)
html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>당뇨병 예방 걷기운동 챗봇</title>
    <style>
        body {font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg,#667eea,#764ba2);
              display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
        .container {background:white;border-radius:20px;box-shadow:0 20px 60px rgba(0,0,0,0.3);
                    width:90%;max-width:800px;display:flex;flex-direction:column;overflow:hidden;}
        .header {background:linear-gradient(135deg,#667eea,#764ba2);color:white;text-align:center;padding:20px;}
        .chat-container {flex:1;overflow-y:auto;padding:20px;background:#f8f9fa;}
        .message {display:flex;gap:10px;margin-bottom:15px;}
        .message.user {flex-direction:row-reverse;}
        .message-avatar {width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;}
        .user .message-avatar {background:linear-gradient(135deg,#667eea,#764ba2);}
        .assistant .message-avatar {background:linear-gradient(135deg,#f093fb,#f5576c);}
        .message-content {padding:12px 15px;border-radius:15px;max-width:70%;}
        .user .message-content {background:linear-gradient(135deg,#667eea,#764ba2);color:white;}
        .assistant .message-content {background:white;box-shadow:0 2px 8px rgba(0,0,0,0.1);}
        .input-container {display:flex;gap:10px;padding:15px;border-top:1px solid #eee;background:white;}
        #userInput {flex:1;padding:12px;border:2px solid #ddd;border-radius:25px;font-size:15px;}
        #sendBtn {padding:12px 25px;border:none;border-radius:25px;background:linear-gradient(135deg,#667eea,#764ba2);
                  color:white;font-weight:600;cursor:pointer;}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h2>🚶‍♂️ 당뇨병 예방 걷기운동 챗봇</h2>
        <p>무엇이든 물어보세요!</p>
    </div>
    <div class="chat-container" id="chatContainer">
        <div class="message assistant">
            <div class="message-avatar">🤖</div>
            <div class="message-content">안녕하세요! 걷기운동과 당뇨병 예방에 대해 궁금한 점이 있나요?</div>
        </div>
    </div>
    <div class="input-container">
        <input type="text" id="userInput" placeholder="질문을 입력하세요..." />
        <button id="sendBtn" onclick="sendMessage()">전송</button>
    </div>
</div>

<script>
const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

function addMessage(text, type) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? '👤' : '🤖';
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(content);
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    addMessage(message, 'user');
    userInput.value = '';
    sendBtn.disabled = true;
    const resp = await fetch('/_stcore/streamlit-gpt', {
        method: 'POST',
        body: JSON.stringify({ message }),
    });
    const data = await resp.json();
    addMessage(data.reply, 'assistant');
    sendBtn.disabled = false;
}
</script>
</body>
</html>
"""

# ✅ HTML 렌더링
components.html(html_code, height=800, scrolling=True)

# ✅ JavaScript → Python 간 통신용 endpoint (Streamlit 핸들링)
import streamlit.runtime.scriptrunner.script_run_context as script_run_context
from streamlit.web.server.websocket_headers import _get_websocket_headers

import tornado.web
from streamlit.web.server import Server

class GPTHandler(tornado.web.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        user_msg = data.get("message", "")
        reply = get_gpt_response(user_msg)
        self.write({"reply": reply})

# ✅ Streamlit에 커스텀 라우트 등록
server = Server.get_current()
if not server.is_running:
    server.start()
app = server._app
if not any(isinstance(h, GPTHandler) for h in app.wildcard_router.rules):
    app.add_handlers(r".*", [(r"/_stcore/streamlit-gpt", GPTHandler)])

