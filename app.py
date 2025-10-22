import streamlit as st
import anthropic
import os

# 페이지 설정
st.set_page_config(
    page_title="당뇨병 예방 걷기운동 챗봇",
    page_icon="🚶‍♂️",
    layout="wide"
)

# 제목 및 설명
st.title("🚶‍♂️ 당뇨병 예방 걷기운동 챗봇")
st.markdown("""
**20대~40대 남성을 위한 맞춤형 걷기운동 가이드**  
당뇨병 예방을 위한 하루 권장 걷기운동량과 건강 정보를 제공합니다.
""")

# API 키 입력
api_key = st.sidebar.text_input("Claude API Key", type="password", help="Anthropic API 키를 입력하세요")

if not api_key:
    st.sidebar.warning("⚠️ API 키를 입력해주세요")
    st.info("👈 왼쪽 사이드바에 Claude API 키를 입력하세요")
    st.stop()

# Claude 클라이언트 초기화
try:
    client = anthropic.Anthropic(api_key=api_key)
except Exception as e:
    st.error(f"API 키 오류: {str(e)}")
    st.stop()

# 시스템 프롬프트
SYSTEM_PROMPT = """당신은 20대 이상 40대 이하 성인 남성을 위한 당뇨병 예방 걷기운동 전문 상담사입니다.

주요 역할:
- 하루 권장 걷기운동량에 대한 정확한 정보 제공
- 개인의 나이, 체중, 활동 수준을 고려한 맞춤형 조언
- 당뇨병 예방을 위한 생활습관 개선 방안 제시
- 걷기운동의 효과와 실천 방법 안내

일반적인 권장사항:
- 하루 30분 이상, 주 5일 이상의 중강도 걷기운동
- 하루 7,000~10,000보 목표
- 식후 10~15분 걷기로 혈당 관리 효과

응답 시 유의사항:
- 친절하고 이해하기 쉬운 한국어로 답변
- 구체적이고 실천 가능한 조언 제공
- 필요시 의료 전문가 상담 권유
- 긍정적이고 동기부여가 되는 톤 유지"""

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("걷기운동에 대해 궁금한 점을 물어보세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Claude API 호출
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=st.session_state.messages
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
        
        except Exception as e:
            error_message = f"오류가 발생했습니다: {str(e)}"
            message_placeholder.error(error_message)
            full_response = error_message
    
    # 어시스턴트 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# 사이드바에 추가 정보
with st.sidebar:
    st.markdown("---")
    st.markdown("### 💡 추천 질문 예시")
    st.markdown("""
    - 하루에 몇 걸음을 걸어야 하나요?
    - 30대 남성의 권장 걷기시간은?
    - 식후 걷기가 왜 중요한가요?
    - 효과적인 걷기 방법은?
    - 당뇨병 예방에 걷기가 얼마나 효과적인가요?
    """)
    
    st.markdown("---")
    st.markdown("### 🔄 대화 초기화")
    if st.button("새로운 대화 시작"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ 안내")
    st.info("""
    이 챗봇은 일반적인 건강 정보를 제공합니다.  
    개인별 맞춤 의료 상담은 전문의와 상담하세요.
    """)
