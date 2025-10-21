import streamlit as st
import time
import pandas as pd

# 🎨 페이지 기본 설정 (가장 첫 줄에서 호출되어야 안전)
st.set_page_config(page_title="당뇨병 걷기운동 가이드 챗봇", page_icon="🏃‍♂️", layout="centered")

# --- 초기화 helper ---
def reset_state():
    st.session_state.step = 0
    st.session_state.userData = {
        "age": None,
        "ageGroup": None,
        "diabetesType": None,
        "activityLevel": None,
        "complications": None
    }
    st.session_state.messages = [
        {"type": "bot", "text": "안녕하세요! 👋 당뇨병 환자를 위한 걷기운동 가이드 챗봇입니다."},
        {"type": "bot", "text": "맞춤형 걷기운동 권장량을 안내해드리겠습니다. 몇 가지 질문에 답변해주세요."},
        {"type": "bot", "text": "현재 나이를 입력해주세요. (예: 35)"}
    ]
    # remove choice UI if present
    if "choices" in st.session_state:
        st.session_state.pop("choices", None)

# 🧠 세션 상태 초기화
if "step" not in st.session_state:
    reset_state()

# 💬 대화 UI 출력
for msg in st.session_state.messages:
    if msg["type"] == "bot":
        st.markdown(f"**🤖 {msg['text']}**")
    else:
        st.markdown(f"<div style='text-align:right;color:#3b82f6;'>🧍‍♂️ {msg['text']}</div>", unsafe_allow_html=True)

# 📊 연령대 분류 함수
def get_age_group(age: int):
    if 30 <= age < 40:
        return "30대"
    elif 40 <= age < 50:
        return "40대"
    elif 50 <= age < 60:
        return "50대"
    elif age >= 60:
        return "60대 이상"
    else:
        return None

# 📋 권장사항 함수 (숫자는 내부적으로 int로 관리)
def get_recommendation(age_group):
    recommendations = {
        "30대": {"steps": 10000, "minutes": "30-40", "intensity": "중강도",
                 "details": "빠르게 걷기, 약간 숨이 찰 정도의 속도", "frequency": "주 5회 이상"},
        "40대": {"steps": 10000, "minutes": "30-40", "intensity": "중강도",
                 "details": "빠르게 걷기, 대화는 가능하지만 노래는 어려운 정도", "frequency": "주 5회 이상"},
        "50대": {"steps": 9000, "minutes": "25-35", "intensity": "중강도",
                 "details": "편안한 속도로 빠르게 걷기", "frequency": "주 5회 이상"},
        "60대 이상": {"steps": 7500, "minutes": "20-30", "intensity": "저-중강도",
                      "details": "편안한 속도로 걷기, 무리하지 않는 범위", "frequency": "주 5회 이상"}
    }
    return recommendations.get(age_group)

# 🧩 단계별 로직
def chatbot_logic(user_input):
    # 안전하게 choices 제거 (텍스트 입력 단계로 이동 시)
    def clear_choices():
        st.session_state.pop("choices", None)

    step = st.session_state.step
    userData = st.session_state.userData
    msgs = st.session_state.messages

    if step == 0:  # 나이 입력
        try:
            age = int(str(user_input).strip())
        except Exception:
            msgs.append({"type": "bot", "text": "숫자로 된 나이를 입력해주세요. 예: 45"})
            return

        age_group = get_age_group(age)
        if not age_group:
            msgs.append({"type": "bot", "text": "지원되는 범위는 30세 이상입니다. 올바른 나이를 입력해주세요."})
            return

        userData["age"] = age
        userData["ageGroup"] = age_group
        msgs.append({"type": "bot", "text": f"{age_group}이시군요. 당뇨병 유형을 선택해주세요."})
        st.session_state.step = 1
        st.session_state.choices = ["1형 당뇨병", "2형 당뇨병"]
        return

    elif step == 1:  # 당뇨병 유형
        if user_input not in ["1형 당뇨병", "2형 당뇨병"]:
            msgs.append({"type": "bot", "text": "1형 또는 2형 중에서 선택해주세요."})
            return
        userData["diabetesType"] = user_input
        msgs.append({"type": "bot", "text": "현재 평소 활동 수준은 어떠신가요?"})
        st.session_state.step = 2
        st.session_state.choices = ["거의 안함", "가끔 (주 1-2회)", "자주 (주 3-4회)", "매우 자주 (주 5회 이상)"]
        return

    elif step == 2:  # 활동 수준
        userData["activityLevel"] = user_input
        msgs.append({"type": "bot", "text": "당뇨 합병증(신장, 망막, 신경병증 등)이 있으신가요?"})
        st.session_state.step = 3
        st.session_state.choices = ["없음", "있음"]
        return

    elif step == 3:  # 합병증 여부
        userData["complications"] = user_input
        msgs.append({"type": "bot", "text": "정보를 분석 중입니다... ⏳"})
        st.session_state.step = 4

        # --- 결과 표시 ---
        rec = get_recommendation(userData.get("ageGroup"))
        if rec is None:
            msgs.append({"type": "bot", "text": "죄송합니다. 내부적으로 권장값을 찾을 수 없습니다. 다시 시도해주세요."})
            # 안전하게 초기화
            reset_state()
            return

        # optional small delay for UX
        time.sleep(0.6)
        msgs.append({"type": "bot", "text": f"📊 {userData['ageGroup']} {userData['diabetesType']} 환자님을 위한 걷기운동 권장사항입니다."})
        time.sleep(0.4)

        # 포맷된 문자열 출력 (쉼표 포함)
        steps_str = f"{rec['steps']:,}"

        msgs.append({"type": "bot", "text":
            f"🚶‍♂️ 하루 권장 걸음 수: {steps_str}걸음\n"
            f"⏱️ 하루 권장 시간: {rec['minutes']}분\n"
            f"💪 운동 강도: {rec['intensity']}\n"
            f"📅 빈도: {rec['frequency']}\n"
            f"✨ 세부사항: {rec['details']}"
        })

        warnings = [
            "• 운동 전후 혈당을 측정하세요",
            "• 저혈당 대비 간식을 준비하세요",
            "• 편안한 운동화를 착용하세요",
            "• 발에 물집이나 상처가 없는지 확인하세요"
        ]
        if userData["complications"] == "있음":
            warnings.append("• 합병증이 있으므로 반드시 담당 의사와 상담 후 운동하세요")
            warnings.append("• 처음에는 짧은 시간부터 시작하세요")
        if userData["activityLevel"] == "거의 안함":
            warnings.append("• 현재 활동량이 적으므로 권장량의 50%부터 시작하세요")
            warnings.append("• 2-4주에 걸쳐 점진적으로 늘려가세요")

        msgs.append({"type": "bot", "text": "⚠️ 중요 주의사항\n" + "\n".join(warnings)})
        msgs.append({"type": "bot", "text": "💡 추가 팁\n• 식후 1~2시간 후 걷기가 혈당 조절에 효과적입니다.\n• 10분씩 나눠 걷기 (예: 10분 x3)도 좋습니다.\n• 스마트폰/워치로 기록을 남기세요."})

        # --- 시각화: bar chart & progress ---
        # 현재 평균(예시)와 권장 비교
        current_avg = 5500  # 예시값 또는 사용자가 업로드한 데이터로 대체 가능
        rec_steps = rec["steps"]

        # store visualization data in session to show after rerun
        st.session_state.visual = {
            "current_avg": current_avg,
            "rec_steps": rec_steps,
            "steps_str": steps_str
        }

        st.session_state.step = 5
        st.session_state.choices = ["새로 시작하기"]
        return

    elif step == 5:
        if user_input == "새로 시작하기":
            reset_state()
            st.experimental_rerun()
        return

# 🧭 사용자 입력 처리 (UI)
user_input = None
choices = st.session_state.get("choices", None)

if choices:
    # radio UI
    user_input = st.radio("선택지를 고르세요 👇", choices, key=f"radio_{st.session_state.step}")
    if st.button("확인"):
        # append user message and process
        st.session_state.messages.append({"type": "user", "text": user_input})
        chatbot_logic(user_input)
        st.experimental_rerun()
else:
    # 텍스트 입력 UI
    user_input = st.text_input("✏️ 메시지를 입력하세요", key=f"text_{st.session_state.step}")
    if st.button("보내기"):
        if user_input.strip():
            st.session_state.messages.append({"type": "user", "text": user_input})
            chatbot_logic(user_input)
            st.experimental_rerun()

# --- 시각화 영역: result visual (별도 렌더링) ---
if st.session_state.get("visual"):
    viz = st.session_state.visual
    st.markdown("---")
    st.subheader("🏃 맞춤 걷기운동 권장 시각화")
    df = pd.DataFrame({
        "카테고리": ["현재 평균(예시)", f"{st.session_state.userData.get('ageGroup', '')} 권장"],
        "걸음 수": [viz["current_avg"], viz["rec_steps"]]
    })
    st.bar_chart(df.set_index("카테고리"))

    progress = min(viz["current_avg"] / viz["rec_steps"], 1.0)
    st.markdown("### 🚶 현재 걸음 대비 권장량 달성률")
    st.progress(progress)
    st.write(f"현재 약 **{progress*100:.1f}%** 수준입니다. (현재: {viz['current_avg']} / 권장: {viz['steps_str']} 걸음)")

# 🟡 주의 문구
st.markdown("---")
st.warning("⚠️ 본 챗봇은 일반적인 정보 제공 목적이며, 의학적 조언을 대체하지 않습니다. 운동 전 반드시 의사와 상담하세요.")
