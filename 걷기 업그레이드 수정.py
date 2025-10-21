import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 🎯 기본 설정
st.set_page_config(page_title="당뇨병 걷기운동 챗봇", page_icon="🏃‍♀️", layout="centered")

# 🧠 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "step" not in st.session_state:
    st.session_state.step = 0
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "age": None,
        "age_group": None,
        "diabetes_type": None,
        "activity_level": None,
        "complications": None,
        "goal_steps": None
    }

# 🎯 나이 그룹 계산 함수
def get_age_group(age):
    if age < 30:
        return None
    elif age < 50:
        return "30~49세"
    elif age < 65:
        return "50~64세"
    else:
        return "65세 이상"

# 🚶‍♂️ 권장 걷기량 계산
def get_recommendation(data):
    base_steps = {
        "30~49세": 9000,
        "50~64세": 8000,
        "65세 이상": 7000
    }

    multiplier = 1.0
    if data["activity_level"] == "활동적":
        multiplier -= 0.1
    elif data["activity_level"] == "비활동적":
        multiplier += 0.2

    if data["complications"] == "있음":
        multiplier -= 0.2

    steps = int(base_steps[data["age_group"]] * multiplier)
    return max(steps, 3000)

# 💬 챗봇 메시지 출력 함수
def add_bot_message(text):
    st.session_state.messages.append({"type": "bot", "text": text})

# 💡 챗봇 로직
def chatbot_logic(user_input):
    step = st.session_state.step
    data = st.session_state.user_data

    if step == 0:
        try:
            age = int(user_input)
            age_group = get_age_group(age)
            if not age_group:
                add_bot_message("30세 이상의 올바른 나이를 입력해주세요.")
                return
            data["age"] = age
            data["age_group"] = age_group
            add_bot_message(f"좋아요. {age_group}군이시군요! 😊")
            add_bot_message("당뇨병 유형을 선택해주세요.")
            st.session_state.step = 1
        except ValueError:
            add_bot_message("숫자로 된 나이를 입력해주세요.")
            return

    elif step == 1:
        if user_input not in ["제1형", "제2형"]:
            add_bot_message("‘제1형’ 또는 ‘제2형’을 입력해주세요.")
            return
        data["diabetes_type"] = user_input
        add_bot_message(f"{user_input} 당뇨병이시군요.")
        add_bot_message("현재 활동 수준을 알려주세요. (활동적 / 보통 / 비활동적)")
        st.session_state.step = 2

    elif step == 2:
        if user_input not in ["활동적", "보통", "비활동적"]:
            add_bot_message("‘활동적’, ‘보통’, 또는 ‘비활동적’ 중 하나로 입력해주세요.")
            return
        data["activity_level"] = user_input
        add_bot_message("좋아요. 😊")
        add_bot_message("합병증이 있으신가요? (있음 / 없음)")
        st.session_state.step = 3

    elif step == 3:
        if user_input not in ["있음", "없음"]:
            add_bot_message("‘있음’ 또는 ‘없음’을 입력해주세요.")
            return
        data["complications"] = user_input
        goal = get_recommendation(data)
        data["goal_steps"] = goal

        add_bot_message("감사합니다! 🚶‍♂️ 이제 결과를 계산할게요...")
        st.session_state.step = 4
        show_recommendation()

    elif step == 5 and user_input in ["예", "다시 시작"]:
        reset_chat()

# 🎯 결과 및 시각화 표시
def show_recommendation():
    data = st.session_state.user_data
    goal = data["goal_steps"]

    add_bot_message(f"📊 {data['age_group']} {data['diabetes_type']} 당뇨병 환자의 권장 걷기량은 하루 {goal:,}보입니다.")
    add_bot_message("참고: 꾸준한 걷기는 혈당 조절에 큰 도움이 됩니다. 😊")

    # 예시 실제 걸음 수 생성 (랜덤 또는 사용자가 입력 가능하게 수정 가능)
    actual_steps = goal * 0.85  # 예: 85% 달성

    # 시각화 데이터
    df = pd.DataFrame({
        "항목": ["실제 걸음 수", "목표 걸음 수"],
        "걸음 수": [actual_steps, goal]
    })

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["항목"],
        y=df["걸음 수"],
        text=df["걸음 수"],
        textposition="auto",
        marker_color=["#7FDBFF", "#FF851B"]
    ))
    fig.update_layout(
        title="하루 걸음 수 vs 목표 걸음 수",
        yaxis_title="걸음 수",
        template="plotly_white"
    )

    st.session_state.recommendation_chart = fig
    st.session_state.step = 5
    add_bot_message("시각화 결과를 아래에서 확인하세요 👇")

# ♻️ 리셋
def reset_chat():
    st.session_state.messages = []
    st.session_state.user_data = {
        "age": None, "age_group": None, "diabetes_type": None,
        "activity_level": None, "complications": None, "goal_steps": None
    }
    st.session_state.step = 0
    add_bot_message("안녕하세요! 👋 당뇨병 환자를 위한 걷기운동 가이드 챗봇입니다.")
    add_bot_message("현재 나이를 입력해주세요. (예: 45)")

# 🧭 인터페이스 렌더링
st.title("🏃‍♀️ 당뇨병 환자 걷기운동 가이드 챗봇")

# 첫 메시지
if len(st.session_state.messages) == 0:
    add_bot_message("안녕하세요! 👋 당뇨병 환자를 위한 걷기운동 가이드 챗봇입니다.")
    add_bot_message("현재 나이를 입력해주세요. (예: 45)")

# 메시지 출력
for msg in st.session_state.messages:
    if msg["type"] == "bot":
        st.markdown(f"🩺 **{msg['text']}**")
    else:
        st.markdown(f"👤 {msg['text']}")

# 입력창
user_input = st.text_input("메시지를 입력하세요", key="user_input")
if st.button("보내기"):
    if user_input.strip():
        st.session_state.messages.append({"type": "user", "text": user_input})
        chatbot_logic(user_input.strip())
        st.rerun()

# 결과 시각화 표시
if "recommendation_chart" in st.session_state:
    st.plotly_chart(st.session_state.recommendation_chart, use_container_width=True)
