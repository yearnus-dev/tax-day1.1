import streamlit as st
import pandas as pd
from datetime import datetime
import difflib
import math

st.set_page_config(page_title="30-50대 걷기", layout="wide")

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
            warning.append("심혈관 질환 의심 시 의사 상담 권장")
            factor = min(factor, 0.7)
        if any(x in c for x in ["고혈압", "혈압"]):
            warning.append("고혈압 시 강도 조절 및 상담 필요")
            factor = min(factor, 0.85)
        if any(x in c for x in ["관절", "무릎", "관절염"]):
            warning.append("관절 문제 시 부드러운 지면·짧은 세션 권장")
            factor = min(factor, 0.8)
        if "임신" in c:
            warning.append("임신 중은 전문의 상담 필요")
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
    notes.append("(세부 조정은 내부 규칙에 따라 계산됨)")

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

# ------------------ UI ------------------
st.title("30–50대 맞춤 걷기 챗봇 🏃‍♀️")
st.caption("입력 조건을 기반으로 권장 걷기 시간과 4주 계획을 생성합니다. 의료 판단은 전문가 상담을 우선하세요.")

with st.sidebar:
    st.header("개인 정보 입력")
    age = st.number_input("나이", min_value=30, max_value=50, value=35)
    sex = st.selectbox("성별", ["여성", "남성", "비공개"])
    weight = st.number_input("체중(kg)", min_value=30.0, max_value=200.0, value=70.0)
    height = st.number_input("키(cm)", min_value=120.0, max_value=230.0, value=170.0)
    activity_level = st.selectbox("평소 활동 수준", ["비활동적", "보통", "매우 활동적"], index=1)
    goal = st.selectbox("주요 목표", ["유지/건강한 생활", "체중 감량", "심폐 지구력 향상"])
    conditions = st.text_input("기저질환/특이사항 (예: 고혈압, 무릎 관절)")
    weekly_override = st.number_input("직접 설정할 주간 목표(분)", min_value=0, value=0)
    st.markdown("---")
    st.info("앱은 교육용입니다. 특이상황(심장질환, 임신 등)은 전문가 상담 후 이용하세요.")

# ------------------ 메인 계산 ------------------
if st.button("권장 시간 계산 및 4주 루틴 생성"):
    # 계산
    rec = compute_recommendation(age, weight, height, sex, activity_level, goal, conditions,
                                 weekly_override if weekly_override > 0 else None)

    # 요약 결과 출력
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

    # 사용자로부터 세션 수와 강도 선호를 받음 (대시보드/루틴 생성 전)
    sessions_per_week = st.slider("주당 세션 수", 3, 7, 5)
    intensity_pref = st.selectbox("선호 강도 유형", ["보통", "인터벌", "빠르게"], index=0)

    # plan 생성 (이제 plan은 확실히 정의됨)
    plan = generate_personalized_4week(age, weight, height, goal, rec['weekly_minutes'], sessions_per_week, intensity_pref)

    # ----------- Fallback Dashboard (plotly 없이) -----------
    st.markdown("### 🧭 개인 맞춤 대시보드 (간략형)")

    # 컬럼 비율을 작게: 화면에서 작게 보이도록 구성
    col1, col2, col3 = st.columns([1, 1, 1])

    # BMI 카드
    with col1:
        bmi_val = rec.get('bmi') or 0
        st.markdown("##### BMI")
        if bmi_val:
            st.metric(label="", value=f"{bmi_val:.1f}")
            norm = max(0, min(100, int((bmi_val - 10) / (40 - 10) * 100)))
            st.progress(norm)
            st.caption(f"{bmi_category(bmi_val)}")
        else:
            st.metric(label="", value="측정불가")
            st.progress(0)
            st.caption("정보 없음")

    # 주간 권장 카드
    with col2:
        weekly_val = rec.get('weekly_minutes', 0)
        st.markdown("##### 주간 권장(분)")
        st.metric(label="", value=f"{weekly_val}분")
        rel = max(0, min(100, int(weekly_val / 300.0 * 100)))
        st.progress(rel)
        st.caption("목표 300분 기준")

    # 일일 평균 카드
    with col3:
        daily_val = rec.get('daily_minutes', 0)
        st.markdown("##### 일일 평균(분)")
        st.metric(label="", value=f"{daily_val}분", delta=f"{daily_val - 30:+} vs 기준(30분)")
        st.progress(min(100, int(daily_val / 60.0 * 100)))
        st.caption("권장: 30분 이상")

    st.markdown("---")

    # 4주간 추세 (여기서 plan은 정의되어 있음)
    st.markdown("#### 📈 4주 진행 추세 (간략)")
    week_labels = [p["주차"] for p in plan]
    totals = [p["주간총시간(분)"] for p in plan]
    df_weeks = pd.DataFrame({"주차": week_labels, "주간총시간(분)": totals}).set_index("주차")
    st.bar_chart(df_weeks, use_container_width=True)

    st.markdown("---")

    # 4주 루틴 상세 출력
    st.subheader("4주 맞춤 루틴 상세")
    for w in plan:
        st.markdown(f"### {w['주차']} — 총 {w['주간총시간(분)']}분 / 1회 {w['1회시간(분)']}분, 세션수 {w['세션수']}")
        for s in w['세부세션']:
            st.write(f"• 세션 {s['세션번호']}: {s['세션시간(분)']}분 — {s['내용']}")
        st.markdown("---")

    # 칼로리 소모 및 걸음 수(요청하신 추가 항목) — 간단 추정
    # 가정: 1분당 걸음수 = 100걸음, 걷기 분당 칼로리 소모 = 4.5 kcal (대략 값, 개인별 차이 큼)
    est_steps_per_min = 100
    est_kcal_per_min = 4.5
    total_week_minutes = rec['weekly_minutes']
    est_week_steps = total_week_minutes * est_steps_per_min
    est_week_kcal = total_week_minutes * est_kcal_per_min

    st.markdown("#### 🔥 예상 주간 소모/걸음 (간략 추정)")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("예상 주간 걸음 수", f"{int(est_week_steps):,} 걸음")
    with c2:
        st.metric("예상 주간 칼로리 소모", f"{int(est_week_kcal):,} kcal (추정)")

    st.markdown("---")

    # CSV 다운로드: 계획을 세션별로 정리해서 제공
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
        st.download_button("CSV 다운로드", data=csv,
                           file_name=f"walk_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                           mime='text/csv')



st.caption("이 앱은 교육·참고용입니다. 특정 증상이나 고위험 상태가 의심되면 의료 전문가 상담을 우선하세요.")
