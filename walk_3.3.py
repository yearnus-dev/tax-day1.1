import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import difflib

st.set_page_config(page_title="30대 걷기 챗봇", layout="wide")

# --- Helper functions ---

def calc_recommended_minutes(age, sex, activity_level, goal):
    """Return recommended daily walking minutes for a typical 30s adult,
    based on public health targets (150–300 min/week moderate-intensity).
    This function uses simple heuristics and explains adjustments.
    """
    # baseline weekly moderate target (minutes)
    baseline_weekly = 150
    if goal == "유지/건강한 생활":
        baseline_weekly = 150
    elif goal == "체중 감량/집중 운동":
        baseline_weekly = 225  # toward upper range
    elif goal == "심폐 지구력 향상":
        baseline_weekly = 200

    # adjust for activity_level
    level_factor = {"매우 활동적": 1.1, "보통": 1.0, "비활동적": 0.9}
    weekly = baseline_weekly * level_factor.get(activity_level, 1.0)

    # convert to daily minutes (7일 기준)
    daily = weekly / 7.0

    # round to nearest whole minute
    return int(round(daily)), int(round(weekly))


def find_best_answer(question, kb, n=1):
    """Find best matching key in knowledge base using difflib."""
    keys = list(kb.keys())
    matches = difflib.get_close_matches(question, keys, n=n, cutoff=0.45)
    # Also try splitting important keywords
    if not matches:
        # try keyword containment
        qlow = question.lower()
        for k in keys:
            if k.lower() in qlow or any(word in k.lower() for word in qlow.split()):
                matches.append(k)
    return matches


# --- Simple knowledge base (Korean) ---
KB = {
    "권장 걷기 시간": (
        "30대 성인을 위한 일반 권장: 보통 성인은 주당 최소 150분의 중간 강도 유산소 운동(또는 75분의 고강도)을 권장합니다.\n\n"
        "이를 하루 단위로 나누면 대략 21~22분/일(주 150분 기준), 목표를 늘리면 30분/일 이상(주 210분)을 권장합니다.\n\n"
        "개별 권장은 체중 목표, 활동 수준, 기저질환 여부에 따라 달라집니다."
    ),
    "걷기 강도와 측정": (
        "중간 강도: 대화는 가능하지만 노래는 부르기 어려운 정도(예: 빠른 보행).\n"
        "고강도: 말하기가 어려울 정도로 숨이 참(예: 빠르게 달리기 또는 매우 빠른 보행).\n"
        "보행 속도 대신 심박수(예: 최대 심박수의 50–70%)나 걸음수(보통 보행은 100걸음/분 전후)를 참고할 수 있습니다."
    ),
    "안전 수칙": (
        "걷기 전 준비운동과 정리운동을 하세요.\n"
        "편한 신발과 적절한 복장을 착용하세요.\n"
        "야간에는 반사 소재를 사용하고, 날씨가 좋지 않으면 실내 걷기를 고려하세요.\n"
        "기저질환(심장병, 고혈압, 당뇨 등)이 있다면 운동 전 의사 상담을 권합니다."
    ),
    "빠르게 늘리는 법": (
        "점진적 증가: 매주 총 시간을 10% 이내로 늘리세요.\n"
        "인터벌: 평상시 속도와 약간 빠른 속도를 번갈아 하세요(예: 3분 걷기, 1분 빠르게 걷기).\n"
        "일상 속 걸음 늘리기: 엘리베이터 대신 계단, 가까운 거리는 도보 이용 등으로 활동량을 증가시키세요."
    ),
    "걸음수 목표": (
        "보통 추천: 초중급자는 하루 7,000~10,000보 목표를 시도해볼 수 있습니다.\n"
        "단, 걸음수는 개인마다 활동 강도 차이가 있으므로 시간·강도와 함께 판단하세요."
    ),
    "임신/특수상황": (
        "임신, 최근 수술, 만성 질환이 있으면 먼저 전문 의료진과 상의하세요.\n"
        "대부분의 경우 가벼운 걷기는 안전하지만 개별 맞춤이 필요합니다."
    ),
}


# --- Layout ---

with st.sidebar:
    st.header("사용자 정보")
    age = st.number_input("나이", value=32, min_value=18, max_value=120, step=1)
    sex = st.selectbox("성별", ["여성", "남성", "기타/비공개"]) 
    activity_level = st.selectbox("평소 활동 수준", ["비활동적", "보통", "매우 활동적"]) 
    goal = st.selectbox("주요 목표", ["유지/건강한 생활", "체중 감량/집중 운동", "심폐 지구력 향상"]) 
    st.markdown("---")
    st.write("앱 기능:\n- 권장 걷기 시간 계산\n- 걷기 계획 생성(간단)\n- 질문형 챗봇(FAQ 기반)\n- 대화 저장 및 다운로드")

# Initialize session state for chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Header
st.title("30대 성인을 위한 걷기 챗봇 🚶‍♂️🚶‍♀️")
st.caption("간단한 권장 시간 계산과 걷기 팁, 계획 생성을 지원합니다. 의료적 조언이 필요한 경우 전문의에게 문의하세요.")

# Recommendation box
recommended_daily, recommended_weekly = calc_recommended_minutes(age, sex, activity_level, goal)

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("당신을 위한 권장 걷기 시간")
    st.write(f"- 대상 연령: {age}세 (설정값)")
    st.write(f"- 권장 주간 목표(중간강도 기준): {recommended_weekly} 분/주")
    st.write(f"- 권장 일일 평균: 약 {recommended_daily} 분/일")
    st.info("표준 권장(세계보건기구 등 권고): 주 150분 중간강도 또는 주 75분 고강도. 개인 사정에 맞춰 조정하세요.")

with col2:
    st.subheader("간단 계획 생성")
    days = st.slider("주 몇 회 걷기 원하나요?", 1, 7, 5)
    make_plan = st.button("걷기 계획 만들기")
    if make_plan:
        per_session = int(round(recommended_weekly / days))
        st.write(f"주 {days}회, 1회당 약 {per_session} 분 걷기(주 {recommended_weekly}분 기준)")
        st.write("예시: 워밍업 5분 → 정상 속도 걷기 (기간) → 쿨다운 5분")

st.markdown("---")

# Chatbot interface
st.subheader("질문하거나 상담해보세요 — (자유 입력 가능)")
user_input = st.text_input("질문을 입력하세요:")

if st.button("전송") and user_input.strip():
    # store user message
    st.session_state.history.append({"role": "user", "text": user_input, "time": datetime.now()})

    # attempt to answer from KB
    matches = find_best_answer(user_input, KB, n=3)
    if matches:
        # return best match
        ans = []
        for m in matches:
            ans.append(f"[{m}]\n{KB[m]}")
        answer_text = "\n\n---\n\n".join(ans)
    else:
        # fallback: simple generative-style reply by combining heuristics
        answer_text = (
            "좋은 질문이에요. 아래는 기본 정보와 권장사항입니다:\n\n"
            f"- 귀하의 권장 일일 걷기 시간(추정): 약 {recommended_daily}분.\n"
            "- 걷기 강도는 중간 강도를 목표로 하세요 — 대화는 되지만 노래하기엔 어려운 정도.\n"
            "- 구체적 계획이나 증상(가슴 통증, 어지러움 등)이 있다면 의료진과 상담하세요.\n\n"
            "혹시 더 구체적인 목표(예: 체중 5kg 감량, 10km 걷기 준비 등)를 알려주시면 상세 계획을 만들어 드립니다."
        )

    st.session_state.history.append({"role": "bot", "text": answer_text, "time": datetime.now()})

# Display chat history
for msg in st.session_state.history[::-1]:
    role = "사용자" if msg["role"] == "user" else "챗봇"
    time_str = msg["time"].strftime("%Y-%m-%d %H:%M:%S")
    if msg["role"] == "bot":
        st.markdown(f"**{role} — {time_str}**\n\n{msg['text']}")
    else:
        st.write(f"**{role} — {time_str}**: {msg['text']}")

st.markdown("---")

# Save/download conversation
if st.session_state.history:
    if st.button("대화 내역 CSV로 저장/다운로드"):
        df = pd.DataFrame([{
            "role": h["role"],
            "text": h["text"],
            "time": h["time"].isoformat()
        } for h in st.session_state.history])
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("CSV 다운로드", data=csv, file_name=f"walkbot_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")

st.caption("이 앱은 교육용이며 개인 맞춤 의료 조언을 대체하지 않습니다.")
