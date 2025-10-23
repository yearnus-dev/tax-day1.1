import streamlit as st
import pandas as pd
from datetime import datetime
import difflib
import math
import random

st.set_page_config(page_title="30-50대 개인화 걷기 챗봇", layout="wide")

# ------------------ Helpers ------------------
def calc_bmi(weight_kg, height_cm):
    if height_cm <= 0:
        return None
    h = height_cm / 100.0
    return round(weight_kg / (h * h), 1)

def age_modifier(age):
    if age < 35:
        return 1.0
    elif age < 40:
        return 0.98
    elif age < 45:
        return 0.96
    elif age < 50:
        return 0.94
    else:
        return 0.92

def bmi_modifier(bmi, goal):
    if bmi is None:
        return 1.0
    if goal == "체중 감량":
        if bmi >= 30:
            return 1.4
        elif bmi >= 25:
            return 1.25
        else:
            return 1.1
    else:
        return 1.0

def activity_modifier(activity_level):
    return {"비활동적": 1.0, "보통": 0.95, "매우 활동적": 0.9}.get(activity_level, 1.0)

def health_condition_adjustments(conditions):
    if not conditions:
        return "", 1.0
    cond = [c.strip().lower() for c in conditions.split(",")]
    warning = []
    factor = 1.0
    for c in cond:
        if not c:
            continue
        if any(x in c for x in ["심장", "심근", "협심증", "심부전"]):
            warning.append("심혈관 질환이 있으면 반드시 의사 상담 후 시작하세요.")
            factor = min(factor, 0.7)
        if any(x in c for x in ["고혈압", "혈압"]):
            warning.append("고혈압이 있으면 운동 강도를 조절하고, 정기적으로 혈압을 확인하세요.")
            factor = min(factor, 0.85)
        if any(x in c for x in ["관절", "무릎", "관절염"]):
            warning.append("관절 문제가 있다면 충격이 적은 지면에서 천천히 늘리세요.")
            factor = min(factor, 0.8)
        if "임신" in c:
            warning.append("임신 중이면 반드시 전문의 상담 후 진행하세요.")
            factor = min(factor, 0.6)
    return "; ".join(warning), factor

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

def compute_recommendation(age, weight, height, sex, activity_level, goal, conditions, weekly_target_override=None):
    base_weekly = 150
    if goal == "심폐 지구력 향상":
        base_weekly = 200
    elif goal == "체중 감량":
        base_weekly = 225

    if weekly_target_override is not None and weekly_target_override > 0:
        base_weekly = weekly_target_override

    bmi = calc_bmi(weight, height) if weight and height else None
    amod = age_modifier(age)
    bmod = bmi_modifier(bmi, goal)
    actmod = activity_modifier(activity_level)
    cond_warning, cond_factor = health_condition_adjustments(conditions)

    weekly = base_weekly * amod * bmod * actmod * cond_factor
    weekly = max(60, round(weekly))
    daily = round(weekly / 7.0)

    notes = []
    if bmi is not None:
        notes.append(f"BMI: {bmi} ({bmi_category(bmi)})")
    if cond_warning:
        notes.append(cond_warning)

    return {
        "weekly_minutes": int(weekly),
        "daily_minutes": int(daily),
        "bmi": bmi,
        "notes": notes
    }

def generate_personalized_4week(age, weight, height, goal, weekly_minutes, sessions_per_week, intensity_pref):
    plan = []
    weekly = weekly_minutes
    for w in range(1, 5):
        if goal == "체중 감량":
            week_factor = 0.9 + 0.05 * w
        elif goal == "심폐 지구력 향상":
            week_factor = 0.92 + 0.06 * w
        else:
            week_factor = 0.85 + 0.04 * w

        week_total = int(round(weekly * week_factor))
        per_session = max(10, int(round(week_total / sessions_per_week)))

        sessions = []
        for s in range(sessions_per_week):
            if goal == "체중 감량":
                if intensity_pref == "인터벌":
                    main = f"3분 보통 + 1분 빠르게 x {max(1, per_session//4)}세트"
                else:
                    main = f"빠른 걷기 {max(0, per_session-10)}분"
            elif goal == "심폐 지구력 향상":
                if intensity_pref == "인터벌":
                    main = f"고강도 1분 + 회복 2분 반복, 총 {max(0, per_session-10)}분"
                else:
                    main = f"빠른 보행 또는 오르막 포함 {max(0, per_session-10)}분"
            else:
                main = f"편안한 속도로 {max(0, per_session-10)}분"

            sessions.append({
                "세션번호": s + 1,
                "세션시간(분)": per_session,
                "내용": f"워밍업 5분 → {main} → 쿨다운 5분"
            })

        plan.append({
            "주차": f"{w}주차",
            "주간총시간(분)": week_total,
            "1회시간(분)": per_session,
            "세션수": sessions_per_week,
            "세부세션": sessions
        })
    return plan

# ------------------ KB ------------------
KB = {
    "권장 걷기 시간": "성인은 주당 최소 150분 중강도 또는 75분 고강도 유산소 운동이 권장됩니다.",
    "강도 정의": "중강도는 말은 가능하지만 노래는 어려운 수준이며, 빠른 걷기가 대표적입니다.",
    "BMI와 걷기": "BMI가 높을수록 걷기 시간을 늘리고, 관절 부담이 적은 지면을 선택하세요.",
    "안전 수칙": "가슴 통증이나 어지러움이 생기면 즉시 중단하고 전문의 상담을 받으세요.",
}

def find_best_answer(question, kb):
    matches = difflib.get_close_matches(question, kb.keys(), n=1, cutoff=0.4)
    if matches:
        base = kb[matches[0]]
    else:
        base = "입력하신 질문에 대한 직접적인 정보는 없지만, 일반적인 원칙을 알려드릴게요."
    # 자유도 높은 답변 스타일 (검색 요약 느낌)
    extras = [
        "건강 전문가들도 걷기를 꾸준히 실천하는 것이 중요하다고 강조합니다.",
        "하루 30분 걷기도 누적하면 큰 건강 효과가 있습니다.",
        "본인의 체력에 맞게 천천히 늘려가세요.",
        "걷기 전후 스트레칭을 꼭 하세요.",
    ]
    return base + " " + random.choice(extras)

# ------------------ UI ------------------
st.title("30–50대 맞춤 걷기 챗봇 (개인화 루틴 생성)")
with st.sidebar:
    st.header("기본 정보")
    age = st.number_input("나이", 30, 50, 40)
    sex = st.selectbox("성별", ["여성", "남성", "비공개"])
    weight = st.number_input("체중(kg)", 30.0, 200.0, 70.0)
    height = st.number_input("키(cm)", 120.0, 230.0, 170.0)
    activity_level = st.selectbox("활동 수준", ["비활동적", "보통", "매우 활동적"], 1)
    goal = st.selectbox("운동 목표", ["유지/건강", "체중 감량", "심폐 지구력 향상"])
    conditions = st.text_input("건강 상태(예: 고혈압, 무릎 통증 등)")
    weekly_override = st.number_input("직접 목표(분, 선택)", 0, 500, 0)

if st.button("권장량 및 루틴 생성"):
    rec = compute_recommendation(age, weight, height, sex, activity_level, goal, conditions, weekly_override if weekly_override > 0 else None)
    st.success(f"주당 권장: {rec['weekly_minutes']}분 (일일 평균 {rec['daily_minutes']}분)")
    if rec['bmi']:
        st.write(f"BMI: {rec['bmi']} ({bmi_category(rec['bmi'])})")
    for n in rec['notes']:
        st.write(f"- {n}")

    st.markdown("---")
    st.subheader("4주 루틴")
    plan = generate_personalized_4week(age, weight, height, goal, rec["weekly_minutes"], 5, "보통")
    for w in plan:
        st.markdown(f"#### {w['주차']} — 주간 총 {w['주간총시간(분)']}분")
        for s in w["세부세션"]:
            st.write(f"• 세션 {s['세션번호']}: {s['내용']}")

st.markdown("---")
st.subheader("질문 또는 추가 요청")
q = st.text_input("예: '하루 몇 분이 좋을까?'")
if st.button("질문 전송") and q.strip():
    st.write(find_best_answer(q, KB))
