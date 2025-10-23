# filename: ask_anything_chatbot.py

import streamlit as st
from openai import OpenAI

# ✅ Streamlit 페이지 기본 설정
st.set_page_config(page_title="무엇이든 물어보세요", page_icon="💬", layout="centered")

# ✅ 제목 및 설명
st.title("💬 무엇이든 물어보세요")
st.caption("GPT가 자유롭게 답변하는 대화형 챗봇입니다.")

# ✅ OpenAI 클라이언트 설정
# - Streamlit Cloud에서는 Settings → Secrets → OPENAI_API_KEY 에 등록
# - 로컬에서는 export OPENAI_API_KEY="키" 로 환경변수 설정 가능
client = OpenAI(api_key=st.secrets["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"])

# ✅ 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "너는 친절하고 유익한 상담형 AI야. 사용자의 질문에 부드럽고 이해하기 쉽게 대답해줘."}
    ]

# ✅ 기존 대화 내용 표시
for msg in st.session_state.messages:
    if msg["role"] != "system":  # system 메시지는 UI에 표시하지 않음
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ✅ 사용자 입력 받기
if prompt := st.chat_input("무엇이든 물어보세요. 예: 운동하면 좋은 점은?"):
    # 사용자 메시지 표시
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # GPT 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("생각 중... 🤔"):
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages
            )
            answer = completion.choices[0].message.content
            st.markdown(answer)

    # 대화 기록 업데이트
    st.session_state.messages.append({"role": "assistant", "content": answer})

# ✅ 하단 안내문
st.markdown("---")
st.caption("💡 본 챗봇은 GPT 모델을 기반으로 하며, 답변은 참고용입니다.")
