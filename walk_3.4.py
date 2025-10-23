import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import difflib

st.set_page_config(page_title="30대 걷기 챗봇", layout="wide")

# --- Helper functions ---

def calc_recommended_minutes(age, sex, activity_level, goal):
    baseline_weekly = 150
    if goal == "유지/건강한 생활":
        baseline_weekly = 150
    elif goal == "체중 감량/집중 운동":
        baseline_weekly = 225
    elif goal == "심폐 지구력 향상":
        baseline_weekly = 200

    level_factor = {"매우 활동적": 1.1, "보통": 1.0, "비활동적": 0.9}
    weekly = baseline_weekly * level_factor.get(activity_level, 1.0)
    daily = weekly / 7.0
    return int(round(daily)), int(round(weekly))


def generate_4week_plan(weekly_minutes, goal):
    base_session = weekly_minutes / 5
    plan = []

    for week in range(1, 5):
        factor = 0.85 + (week - 1) * 0.05
        session_time = int(round(base_session * factor))

        if goal == "유지/건강한 생활":
            intensity = "편안한 속도로 꾸준히 걷기"
            tip = "대화 가능한 속도로 하루 일상 속 걷기 습관 형성"
        elif goal == "체중 감량/집중 운동":
            intensity = "빠른 속도 + 인터벌 포함"
            tip = "3분 보통 속도 + 1분 빠른 속도 인터벌 4세트, 주말엔 장거리 1회"
        else:
            intensity = "심폐 강화용 빠른 걷기"
            tip = "빠른 보행 + 오르막 또는 계단 걷기, 심박수 70% 유지"

        plan.append({
            "주차": f"{week}주차",
            "주간 총 시간": int(round(weekly_minutes * factor)),
            "1회 운동 시간": session_time,
            "운동 강도": intensity,
            "설명": f"워밍업 5분 → 메인 {session_time - 10}분 → 쿨다운 5분",
            "포인트": tip
        })

    df = pd.DataFrame(plan)
    return df


def find_best_answer(question, kb, n=1):
    keys = list(kb.keys())
    matches = difflib.get_close_matches(question, keys, n=n, cutoff=0.45)
    if not matches:
        qlow = question.lower()
        for k in keys:
            if k.lower() in qlow or any(word in k.lower() for word in qlow.split()):
                matches.append(k)
    return matches


KB = {
    "권장 걷기 시간": (
        "30대 성인을 위한 일반 권장: 보통 성인은 주당 최소 150분의 중간 강도 유산소 운동(또는 75분의 고강도)을 권장합니다.\n\n"
        "이를 하루 단위로 나누면 대략 21~22분/일(주 150분 기준), 목표를 늘리면 30분/일 이상(주 210분)을 권장합니다."
    ),
    "걷기 강도와 측정": (
        "중간 강도: 대화는 가능하지만 노래는 부르기 어려운 정도.\n"
        "고강도: 말하기가 어려울 정도로 숨이 참 정도."
    ),
    "안전 수칙": (
        "걷기 전후 스트레칭을 하세요.\n"
        "편한 신발과 복장 착용. 날씨가 안 좋으면 실내 걷기 권장."
    ),
    "빠르게 늘리는 법": (
        "매주 운동량을 10% 이내로 증가시키세요.\n"
        "인터벌 걷기: 평속 3분 + 빠른속도 1분 반복."
    ),
    "걸음수 목표": (
        "하루 7,000~10,000보 권장. 체중 감량 시 12,000보 이상 가능."
    ),
    "4주 걷기 루틴": (
        "**4주 걷기 루틴 예시 (목표별)**\n\n"
        "- **유지/건강한 생활:** 매일 25~35분, 주 5회 걷기 (편안한 속도).\n"
        "- **체중 감량/집중 운동:** 주 5회, 1회 35~45분 빠른 걷기 + 인터벌(1분 빠르게, 3분 보통).\n"
        "- **심폐 지구력 향상:** 주 4~6회, 오르막/계단 포함 30~50분 걷기.\n\n"
        "매주 주말엔 회복용 산책 또는 스트레칭일을 포함하세요."
    )
}

with st.sidebar:
    st.header("사용자 정보")
    age = st.number_input("나이", value=32, min_value=18, max_value=120)
    sex = st.selectbox("성별", ["여성", "남성", "기타/비공개"])
    activity_level = st.selectbox("평소 활동 수준", ["비활동적", "보통", "매우 활동적"])
    goal = st.selectbox("주요 목표", ["유지/건강한 생활", "체중 감량/집중 운동", "심폐 지구력 향상"])
    st.markdown("---")
    st.write("앱 기능:\n- 권장 걷기 시간 계산\n- 4주 루틴 생성(목표별)\n- 질문형 챗봇\n- 대화 다운로드")

if "history" not in st.session_state:
    st.session_state.history = []

st.title("30대 성인을 위한 걷기 챗봇 🚶‍♀️🚶‍♂️")

recommended_daily, recommended_weekly = calc_recommended_minutes(age, sex, activity_level, goal)

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("당신을 위한 권장 걷기 시간")
    st.write(f"- 주간 목표: {recommended_weekly}분 (일일 약 {recommended_daily}분)")
    st.info("세계보건기구 권장: 주 150분 중간강도 또는 75분 고강도 운동.")

with col2:
    st.subheader("4주 걷기 루틴 생성")
    if st.button("4주 루틴 보기"):
        df = generate_4week_plan(recommended_weekly, goal)
        st.dataframe(df, use_container_width=True)
        st.success(f"{goal} 목표에 맞춘 4주 루틴이 생성되었습니다!")

st.markdown("---")

st.subheader("질문해보세요")
user_input = st.text_input("질문을 입력하세요:")

if st.button("전송") and user_input.strip():
    st.session_state.history.append({"role": "user", "text": user_input, "time": datetime.now()})
    matches = find_best_answer(user_input, KB, n=3)
    if matches:
        ans = []
        for m in matches:
            ans.append(f"[{m}]\n{KB[m]}")
        answer_text = "\n\n---\n\n".join(ans)
    else:
        answer_text = f"귀하의 목표({goal})에 맞춘 일일 권장 걷기 시간은 약 {recommended_daily}분입니다. 4주 루틴을 함께 참고하세요."
    st.session_state.history.append({"role": "bot", "text": answer_text, "time": datetime.now()})

for msg in st.session_state.history[::-1]:
    role = "사용자" if msg["role"] == "user" else "챗봇"
    time_str = msg["time"].strftime("%Y-%m-%d %H:%M:%S")
    if msg["role"] == "bot":
        st.markdown(f"**{role} — {time_str}**\n\n{msg['text']}")
    else:
        st.write(f"**{role} — {time_str}**: {msg['text']}")

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
