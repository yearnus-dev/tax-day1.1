import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="당뇨병 예방 걷기운동 대시보드", page_icon="🚶‍♂️", layout="wide")

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"type": "bot", "text": "안녕하세요! 👋 걷기운동에 대해 궁금한 점을 물어보세요."}
    ]
if 'current_steps' not in st.session_state:
    st.session_state.current_steps = 6543

# CSS 스타일
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .chat-message {
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 80%;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        text-align: right;
    }
    .bot-message {
        background: white;
        color: #333;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .tip-box {
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #00acc1;
        margin-top: 20px;
    }
    .chart-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 30px;
        border-radius: 5px;
        transition: width 0.3s;
    }
    .chart-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px;'>
    <h1>🚶‍♂️ 당뇨병 예방 걷기운동 대시보드</h1>
    <p style='opacity: 0.9; font-size: 16px;'>실시간 통계 + AI 챗봇 가이드</p>
</div>
""", unsafe_allow_html=True)

# KPI 메트릭
col1, col2, col3, col4 = st.columns(4)

daily_goal = 10000
current_steps = st.session_state.current_steps
progress = min(100, (current_steps / daily_goal) * 100)

with col1:
    st.metric("🚶 오늘 걸음 수", f"{current_steps:,}보", f"목표: {daily_goal:,}보")

with col2:
    st.metric("🎯 달성률", f"{progress:.0f}%", "일일 목표 기준")

with col3:
    st.metric("⏱️ 운동 시간", "42분", "권장: 30분 이상")

with col4:
    st.metric("🔥 소모 칼로리", "287 kcal", "+15 kcal")

# 진행률 바
st.markdown("### 📊 일일 목표 진행률")
st.progress(progress / 100)
st.caption(f"{current_steps:,} / {daily_goal:,}보 ({progress:.1f}%)")

st.markdown("---")

# 차트 섹션 (Streamlit 기본 차트 사용)
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("### 📈 주간 걸음 수 추이")
    weekly_data = pd.DataFrame({
        '요일': ['월', '화', '수', '목', '금', '토', '일'],
        '걸음 수': [8234, 9821, 7453, 10234, 8976, 11543, 6543],
        '목표': [10000] * 7
    })
    
    st.bar_chart(weekly_data.set_index('요일')[['걸음 수', '목표']])

with chart_col2:
    st.markdown("### ⏰ 시간대별 활동량")
    hourly_data = pd.DataFrame({
        '시간': ['06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
        '걸음 수': [1200, 800, 1500, 900, 1800, 343]
    })
    
    st.line_chart(hourly_data.set_index('시간'))

st.markdown("---")

# 챗봇 + 도넛차트 섹션
chat_col1, chat_col2 = st.columns([2, 1])

with chat_col2:
    st.markdown("### 🎯 목표 달성률")
    
    # 간단한 도넛 차트 대체 (진행률 표시)
    st.markdown(f"""
    <div style='text-align: center; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
        <div style='width: 200px; height: 200px; margin: 0 auto; border-radius: 50%; 
                    background: conic-gradient(#667eea 0% {progress}%, #e0e7ff {progress}% 100%);
                    display: flex; align-items: center; justify-content: center;'>
            <div style='width: 140px; height: 140px; background: white; border-radius: 50%; 
                        display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                <h1 style='color: #667eea; margin: 0;'>{progress:.0f}%</h1>
                <p style='color: #666; margin: 5px 0 0 0; font-size: 14px;'>오늘 달성률</p>
            </div>
        </div>
        <div style='margin-top: 20px;'>
            <div style='display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 5px;'>
                <div style='width: 15px; height: 15px; background: #667eea; border-radius: 3px;'></div>
                <span>달성: {current_steps:,}보</span>
            </div>
            <div style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
                <div style='width: 15px; height: 15px; background: #e0e7ff; border-radius: 3px;'></div>
                <span>남은 목표: {max(0, daily_goal - current_steps):,}보</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with chat_col1:
    st.markdown("### 💬 AI 걷기운동 가이드")
    
    # 챗봇 메시지 표시
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg['type'] == 'user':
                st.markdown(f"<div class='chat-message user-message'>{msg['text']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-message bot-message'>{msg['text']}</div>", unsafe_allow_html=True)
    
    # 챗봇 응답 함수
    def generate_response(user_message):
        msg = user_message.lower()
        
        if '걸음' in msg or '보수' in msg:
            return "20대~40대 남성의 당뇨병 예방을 위한 하루 권장 걸음 수는 약 7,000~10,000보입니다.\n\n• 최소 목표: 7,000보\n• 이상적 목표: 10,000보\n• 현재 대시보드에서 실시간으로 걸음 수를 확인하실 수 있습니다!"
        elif '시간' in msg or '30대' in msg or '20대' in msg or '40대' in msg:
            return "20대~40대 남성의 권장 걷기시간은 하루 30분 이상, 주 5일 이상입니다.\n\n한 번에 30분이 어렵다면 10분씩 3회로 나눠도 좋습니다. 위 차트에서 주간 운동 패턴을 확인해보세요!"
        elif '식후' in msg or '밥' in msg or '식사' in msg:
            return "식후 걷기는 혈당 급상승을 막고 인슐린 감수성을 높이는 데 도움됩니다.\n\n• 식사 후 10~15분 걷기\n• 저녁 식사 후 걷기가 특히 효과적입니다.\n• 시간대별 차트에서 12시, 18시 이후 활동량을 늘려보세요!"
        elif '방법' in msg or '어떻게' in msg or '효과적' in msg:
            return "효과적인 걷기 운동 방법:\n\n1. 가슴을 펴고 시선은 전방 15m\n2. 팔은 자연스럽게 흔들기\n3. 발뒤꿈치부터 착지 후 발가락으로 밀기\n4. 분당 100~120보 속도 유지"
        elif '당뇨' in msg or '예방' in msg or '효과' in msg:
            return "걷기운동은 당뇨병 예방에 매우 효과적입니다!\n\n• 혈당 조절 개선\n• 체중 관리\n• 심혈관 건강 향상\n• 인슐린 감수성 증가"
        else:
            return "안녕하세요! 걷기운동에 대해 더 궁금한 점을 물어보세요.\n\n추천 질문: '하루 권장 걸음 수', '식후 걷기 효과', '효과적인 걷기 방법'"
    
    # 추천 질문 버튼
    st.markdown("**💡 추천 질문:**")
    button_cols = st.columns(2)
    with button_cols[0]:
        if st.button("하루 권장 걸음 수", use_container_width=True):
            st.session_state.messages.append({"type": "user", "text": "하루 권장 걸음 수는?"})
            response = generate_response("하루 권장 걸음 수는?")
            st.session_state.messages.append({"type": "bot", "text": response})
            st.rerun()
    with button_cols[1]:
        if st.button("식후 걷기 효과", use_container_width=True):
            st.session_state.messages.append({"type": "user", "text": "식후 걷기 효과는?"})
            response = generate_response("식후 걷기 효과는?")
            st.session_state.messages.append({"type": "bot", "text": response})
            st.rerun()
    
    button_cols2 = st.columns(2)
    with button_cols2[0]:
        if st.button("효과적인 걷기 방법", use_container_width=True):
            st.session_state.messages.append({"type": "user", "text": "효과적인 걷기 방법은?"})
            response = generate_response("효과적인 걷기 방법은?")
            st.session_state.messages.append({"type": "bot", "text": response})
            st.rerun()
    with button_cols2[1]:
        if st.button("당뇨병 예방 효과", use_container_width=True):
            st.session_state.messages.append({"type": "user", "text": "당뇨병 예방 효과는?"})
            response = generate_response("당뇨병 예방 효과는?")
            st.session_state.messages.append({"type": "bot", "text": response})
            st.rerun()
    
    st.markdown("---")
    
    # 사용자 입력
    user_input = st.text_input("궁금한 점을 물어보세요...", key="chat_input", placeholder="예: 하루에 몇 걸음을 걸어야 하나요?")
    
    if st.button("💬 전송", use_container_width=True):
        if user_input.strip():
            st.session_state.messages.append({"type": "user", "text": user_input})
            response = generate_response(user_input)
            st.session_state.messages.append({"type": "bot", "text": response})
            st.rerun()

# 건강 팁 섹션
st.markdown("""
<div class='tip-box'>
    <h3>💡 오늘의 건강 팁</h3>
    <ul style='margin-top: 10px; line-height: 1.8;'>
        <li>✅ 식후 10-15분 걷기로 혈당 관리를 시작하세요</li>
        <li>✅ 하루 10,000보 목표를 3회로 나눠서 달성해보세요</li>
        <li>✅ 편안한 운동화 착용으로 발 건강을 지키세요</li>
        <li>✅ 걷기 전후 스트레칭으로 부상을 예방하세요</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# 자동 새로고침 버튼 (걸음 수 시뮬레이션)
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    if st.button("🔄 걸음 수 업데이트 (시뮬레이션)", use_container_width=True):
        st.session_state.current_steps = min(daily_goal, st.session_state.current_steps + random.randint(50, 200))
        st.rerun()

st.markdown("---")
st.caption("⚠️ 본 대시보드는 일반적인 정보 제공 목적이며, 의학적 조언을 대체하지 않습니다.")
