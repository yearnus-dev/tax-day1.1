import streamlit as st
import pandas as pd
from datetime import datetime
import difflib

st.set_page_config(page_title="30–50대 개인 맞춤 걷기 챗봇", layout="wide")

# ------------------ Helper Functions ------------------

def calc_bmi(weight, height):
    if height <= 0:
        return None
    return round(weight / ((height / 100) ** 2), 1)

def bmi_category(bmi):
    if bmi is None:
        return "측정불가"
    if bmi < 18.5:
        return "저체중"
    elif bmi < 23:
        return "정상"
    elif bmi < 25:
        return "과체중(경계)"
    elif bmi < 30:
        return "과체중"
    else:
        return "비만"

def age_modifier(age):
    if age < 35:
        return 1.0
    elif age < 40:
        return 0.97
    elif age < 45:
        return 0.95
    elif age < 50:
        return 0.93
    else:
        return 0.9

def activity_modifier(level):
    return {"비활동적": 1.0, "보통": 0.95, "매우 활동적": 0.9}.get(level, 1.0)

def bmi_modifier(bmi, goal):
    if goal == "체중 감량":
        if bmi >= 30: return 1.4
        elif bmi >= 25: return 1.25
        else: return 1.1
    return 1.0

def cardio_metabolic_adjustment(bpi, rhr, glucose):
    """혈압, 심박수, 혈당 상태에 따른 보정"""
    factor = 1.0
    notes = []

    # 혈압
    if bpi == "경계":
        factor *= 0.95
        notes.append("혈압 경계 수준 — 운동 강도 약간 완화 권장")
    elif bpi == "고혈압":
        factor *= 0.85
        notes.append("고혈압 상태 — 짧은 세션, 저강도 걷기 권장")

    # 심박수
    if rhr > 90:
        factor *= 0.85
        notes.append(f"안정시 심박수 {rhr}bpm — 심폐 부담 가능성, 강도 완화")
    elif rhr > 80:
        factor *= 0.9
        notes.append(f"심박수 {rhr}bpm — 점진적 강도 증가 필요")

    # 혈당
    if glucose == "경계":
        factor *= 0.95
        notes.append("혈당 경계 수준 — 식후 10분 걷기 습관 권장")
    elif glucose == "고혈당":
        factor *= 0.85
        notes.append("혈당 높음 — 짧고 자주 걷기(예: 하루 3회 10분) 권장")

    return factor, notes

def compute_recommendation(age, weight, height, sex, activity_level, goal, bpi, rhr, glucose):
    base_weekly = 150
    if goal == "체중 감량":
        base_weekly = 220
    elif goal == "심폐 지구력 향상":
        base_weekly = 200

    bmi = calc_bmi(weight, height)
    amod = age_modifier(age)
    actmod = activity_modifier(activity_level)
    bmod = bmi_modifier(bmi, goal)
    cm_factor, cm_notes = cardio_metabolic_adjustment(bpi, rhr, glucose)

    weekly = base_weekly * amod * actmod * bmod * cm_factor
    weekly = max(60, int(round(weekly)))
    daily = int(round(weekly / 7))

    notes = []
    notes.append(f"BMI: {bmi} ({bmi_category(bmi)})")
    notes.extend(cm_notes)
    notes.append("(조정계수는 연령, 활동수준, BMI, 건강지표를 반영했습니다.)")

    return {"weekly": weekly, "daily": daily, "notes": notes}

def generate_4week_plan(goal, weekly_minutes, sessions_per_week, condition_notes):
    plan = []
    for week in range(1, 5):
        if goal == "체중 감량":
            factor = 0.9 + 0.05 * week
        elif goal == "심폐 지구력 향상":
            factor = 0.92 + 0.06 * week
        else:
            factor = 0.85 + 0.04 * week

        total = int(weekly_minutes * factor)
        per_session = int(total / sessions_per_week)
        note = condition_notes[0] if condition_notes else ""

        plan.append({
            "주차": f"{week}주차",
            "주간 총 시간(분)": total,
            "1회 평균(분)": per_session,
            "추천 내용": f"워밍업 5분 + 주행 {per_session-10}분 + 쿨다운 5분 — {note}"
        })
    return plan

def find_best_answer(q, kb):
    matches = difflib.get_close_matches(q, list(kb.keys()), n=2, cutoff=0.45)
    if not matches:
        qlow = q.lower()
        for k in kb.keys():
            if k.lower() in qlow or any(word in k.lower() for word in qlow.split()):
                matches.append(k)
    return matches

# ------------------ Knowledge Base ------------------
KB = {
    "걷기 권장 시간": "성인(30~50대)의 일반 권장은 주당 150~300분의 중강도 유산소 운동입니다.",
    "고혈압 운동 요령": "짧은 세션(10~20분)을 하루 2~3회로 나누어 꾸준히 걷는 것이 안전합니다.",
    "심박수와 강도": "안정시 심박수가 80bpm 이상이면 초기에는 중강도 이하(말은 되지만 노래는 힘든 정도)로 시작하세요.",
    "혈당 조절을 위한 걷기": "식후 10~30분 내에 10분 이상 걷는 것이 혈당 안정에 도움됩니다."
}

# ------------------ UI ------------------
st.title("🏃‍♂️ 30–50대 개인 맞춤 걷기 챗봇")
st.caption("입력하신 신체 및 건강 정보를 기반으로 하루·주간 권장 걷기 시간과 맞춤 루틴을 제안합니다.")

with st.sidebar:
    st.header("🧍‍♀️ 기본 정보 입력")
    age = st.number_input("나이", 30, 50, 40)
    sex = st.selectbox("성별", ["여성", "남성", "비공개"])
    weight = st.number_input("체중(kg)", 30.0, 150.0, 70.0)
    height = st.number_input("키(cm)", 120.0, 220.0, 170.0)
    activity = st.selectbox("활동 수준", ["비활동적", "보통", "매우 활동적"])
    goal = st.selectbox("운동 목표", ["유지/건강한 생활", "체중 감량", "심폐 지구력 향상"])

    st.markdown("### ❤️ 건강 지표")
    bpi = st.selectbox("혈압 상태", ["정상", "경계", "고혈압"])
    rhr = st.number_input("안정시 심박수(bpm)", 40, 120, 75)
    glucose = st.selectbox("혈당 상태", ["정상", "경계", "고혈당"])

if st.button("권장 걷기 시간 계산"):
    result = compute_recommendation(age, weight, height, sex, activity, goal, bpi, rhr, glucose)
    st.subheader("📊 개인 맞춤 결과")
    st.write(f"- 주간 권장 시간: **{result['weekly']}분**")
    st.write(f"- 일일 평균: **{result['daily']}분**")
    for n in result["notes"]:
        st.write("•", n)

    st.markdown("---")
    st.subheader("🏅 4주 맞춤 루틴")
    sessions = st.slider("주당 세션 수", 3, 7, 5)
    plan = generate_4week_plan(goal, result["weekly"], sessions, result["notes"])

    for p in plan:
        st.markdown(f"**{p['주차']}** — 총 {p['주간 총 시간(분)']}분, 1회 {p['1회 평균(분)']}분")
        st.caption(p["추천 내용"])
    st.markdown("---")

# ------------------ 자유 질문 ------------------

st.markdown("---")
st.subheader("질문 또는 추가 요청 (자유 입력)")
q = st.text_input("예: '40대 여성인데 체중 감량을 위해 하루 몇 분 걸어야 해요?' 또는 '빠른 걷기 루틴 알려줘'")

if st.button("질문 전송") and q.strip():
    st.write(generate_flexible_answer(q, rec))

st.caption("💬 자유도 높은 답변 생성형 알고리즘 적용 (네이버·구글식 자연 응답)")
