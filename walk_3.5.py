import streamlit as st
import pandas as pd
from datetime import datetime
import difflib
import math

st.set_page_config(page_title="30-50대 개인화 걷기 챗봇", layout="wide")

# ------------------ Helpers ------------------

def calc_bmi(weight_kg, height_cm):
    if height_cm <= 0:
        return None
    h = height_cm / 100.0
    return round(weight_kg / (h * h), 1)


def age_modifier(age):
    # small conservative modifier: older adults may progress slightly slower
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
    # If user aims for weight loss and BMI >= 25, recommend higher weekly minutes
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
    # returns a string warning and a safety factor (<=1 reduces recommended volume)
    if not conditions:
        return "", 1.0
    cond = [c.strip().lower() for c in conditions.split(",")]
    warning = []
    factor = 1.0
    for c in cond:
        if not c:
            continue
        if any(x in c for x in ["심장", "심근", "협심증", "심부전"]):
            warning.append("심혈관 질환이 의심되거나 진단된 경우, 운동 시작 전 의사 상담 권장")
            factor = min(factor, 0.7)
        if any(x in c for x in ["고혈압", "혈압"]):
            warning.append("고혈압이 있으면 강도 조절과 의사 상담을 권장")
            factor = min(factor, 0.85)
        if any(x in c for x in ["관절", "무릎", "관절염"]):
            warning.append("관절 문제가 있으면 충격을 줄이는 방식(부드러운 지면, 짧은 세션) 권장")
            factor = min(factor, 0.8)
        if "임신" in c:
            warning.append("임신 중일 경우 전문의 상담 필요")
            factor = min(factor, 0.6)
    return "; ".join(warning), factor


def compute_recommendation(age, weight, height, sex, activity_level, goal, conditions, weekly_target_override=None):
    # Base weekly target: WHO 150 min moderate. Allow user override.
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

    # combine modifiers (multiply)
    weekly = base_weekly * amod * bmod * actmod * cond_factor
    weekly = max(60, round(weekly))  # floor minimum
    daily = round(weekly / 7.0)

    notes = []
    if bmi is not None:
        notes.append(f"BMI: {bmi} ({bmi_category(bmi)})")
    if cond_warning:
        notes.append(cond_warning)
    notes.append(f"조정 계수: 연령 {amod:.2f} x 체형/목표 {bmod:.2f} x 활동수준 {actmod:.2f} x 건강요인 {cond_factor:.2f}" if False else "(세부 조정은 내부 규칙에 따라 계산됨)")

    return {
        "weekly_minutes": int(weekly),
        "daily_minutes": int(daily),
        "bmi": bmi,
        "notes": notes
    }


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


def generate_personalized_4week(age, weight, height, goal, weekly_minutes, sessions_per_week, intensity_pref):
    # Build progressive 4-week plan. intensity_pref: '보통','인터벌','빠르게'
    plan = []
    weekly = weekly_minutes
    for w in range(1, 5):
        # progressive increase depending on goal
        if goal == "체중 감량":
            week_factor = 0.9 + 0.05 * w
        elif goal == "심폐 지구력 향상":
            week_factor = 0.92 + 0.06 * w
        else:
            week_factor = 0.85 + 0.04 * w

        week_total = int(round(weekly * week_factor))
        per_session = max(10, int(round(week_total / sessions_per_week)))

        # Build session breakdown
        sessions = []
        for s in range(sessions_per_week):
            if goal == "체중 감량":
                if intensity_pref == "인터벌":
                    # Example interval session
                    main = f"인터벌: 3분 보통 + 1분 빠르게 x {max(1, per_session//4)}세트"
                else:
                    main = f"지속 빠른 걷기 {max(0, per_session-10)}분"
            elif goal == "심폐 지구력 향상":
                if intensity_pref == "인터벌":
                    main = f"인터벌(고강도) 1분/2분 반복, 총 {max(0, per_session-10)}분"
                else:
                    main = f"빠른 보행/오르막 포함 {max(0, per_session-10)}분"
            else:
                main = f"편안한 속도 지속 {max(0, per_session-10)}분"

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


def find_best_answer(question, kb, n=2):
    keys = list(kb.keys())
    matches = difflib.get_close_matches(question, keys, n=n, cutoff=0.45)
    if not matches:
        qlow = question.lower()
        for k in keys:
            if k.lower() in qlow or any(word in k.lower() for word in qlow.split()):
                matches.append(k)
    return matches

# ------------------ Knowledge base ------------------
KB = {
    "권장 걷기 시간": "일반 권장: 주당 최소 150분 중간강도(또는 75분 고강도). 연령(30-50대) 전반적 권장량은 동일하지만 개인 상태에 따라 조정 필요.",
    "강도 정의": "중간강도: 말은 가능하지만 노래는 어려움(예: 빠른 걷기). 고강도: 말하기 어려움(예: 달리기, 매우 빠른 보행).",
    "BMI와 권장": "BMI가 높을수록 체중 감량 목표의 경우 더 많은 유산소량(예: 주 200분 이상)을 권할 수 있습니다. 다만 관절이나 심장 문제는 고려 필요합니다.",
    "안전 수칙": "가슴 통증, 심한 어지러움, 과호흡이 있으면 즉시 중단하고 의료진 상담 요망. 운동 전에 준비운동, 후에 정리운동을 하세요.",
}

# ------------------ UI ------------------
st.title("30–50대 맞춤 걷기 챗봇 \n(나이·체중·건강조건 기반 개인화)")
st.caption("입력하신 조건을 바탕으로 권장 걷기 시간과 4주 계획을 생성합니다. 의료적 판단은 전문가 상담을 우선하세요.")

with st.sidebar:
    st.header("개인 정보 입력")
    age = st.number_input("나이", min_value=30, max_value=50, value=35)
    sex = st.selectbox("성별", ["여성", "남성", "비공개"])
    weight = st.number_input("체중(kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
    height = st.number_input("키(cm)", min_value=120.0, max_value=230.0, value=170.0, step=0.1)
    activity_level = st.selectbox("평소 활동 수준", ["비활동적", "보통", "매우 활동적"], index=1)
    goal = st.selectbox("주요 목표", ["유지/건강한 생활", "체중 감량", "심폐 지구력 향상"])
    conditions = st.text_input("기저질환/특이사항 (콤마로 구분, 예: 고혈압, 무릎 관절)")
    weekly_override = st.number_input("직접 설정할 주간 목표(분, 원하면 입력)", min_value=0, value=0)
    st.markdown("---")
    st.info("앱은 교육용입니다. 만약 심장질환·임신 등 특이상황이 있으면 전문가 상담을 먼저 받으세요.")

# Compute recommendation
if st.button("권장 시간 계산 및 4주 루틴 생성"):
    rec = compute_recommendation(age, weight, height, sex, activity_level, goal, conditions, weekly_override if weekly_override>0 else None)
    st.subheader("개인화 권장 결과")
    st.write(f"- 주간 권장(추정): {rec['weekly_minutes']} 분/주")
    st.write(f"- 일일 평균(추정): {rec['daily_minutes']} 분/일")
    if rec['bmi'] is not None:
        st.write(f"- BMI: {rec['bmi']} ({bmi_category(rec['bmi'])})")
    if rec['notes']:
        st.write("- 참고/주의사항:")
        for n in rec['notes']:
            st.write(f"  - {n}")

    st.markdown("---")
    st.subheader("4주 맞춤 루틴 옵션")
    sessions_per_week = st.slider("주당 세션 수", 3, 7, 5)
    intensity_pref = st.selectbox("선호 강도 유형", ["보통", "인터벌", "빠르게"], index=0)

    plan = generate_personalized_4week(age, weight, height, goal, rec['weekly_minutes'], sessions_per_week, intensity_pref)

    # Show plan in readable format
    for w in plan:
        st.markdown(f"### {w['주차']} — 주간 총 {w['주간총시간(분)']}분, 1회 약 {w['1회시간(분)']}분, 세션수 {w['세션수']}")
        for s in w['세부세션']:
            st.write(f"• 세션 {s['세션번호']}: {s['세션시간(분)']}분 — {s['내용']}")
        st.markdown("---")

    # Exportable CSV summary
    if st.button("루틴 요약 CSV로 다운로드"):
        rows = []
        for w in plan:
            for s in w['세부세션']:
                rows.append({
                    '주차': w['주차'],
                    '세션번호': s['세션번호'],
                    '세션시간(분)': s['세션시간(분)'],
                    '내용': s['내용']
                })
        df = pd.DataFrame(rows)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("CSV 다운로드", data=csv, file_name=f"walk_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime='text/csv')

# Chatbot-style free Q&A
st.markdown("---")
st.subheader("질문 또는 추가 요청 (자유 입력)")
q = st.text_input("질문을 입력하세요 (예: 'BMI가 27이면 얼마나 걸어야 하나요?')")
if st.button("질문 전송") and q.strip():
    matches = find_best_answer(q, KB, n=3)
    if matches:
        for m in matches:
            st.markdown(f"**{m}**: {KB[m]}")
    else:
        st.write("죄송해요 — 해당 질문에 딱 맞는 항목을 찾지 못했습니다. 입력하신 개인 정보를 기반으로 권장안을 생성해 보세요.")

st.caption("이 앱은 교육·참고용입니다. 특정 증상이나 고위험 상태가 의심되면 의료 전문가 상담을 우선하세요.")
