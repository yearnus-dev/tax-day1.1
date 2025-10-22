import streamlit as st
import requests
import datetime as dt
import json
import os

# -------- WHO 권장량 로직 --------
def recommended_minutes_per_day(age, experience):
    base = 30
    if age >= 50:
        base -= 5
    if experience == "none":
        base -= 5
    elif experience == "advanced":
        base += 10
    return max(base, 15)

# -------- 누적 달성률 계산 --------
def calculate_achievement(records, daily_target):
    today = dt.date.today()
    this_week = [r for r in records if (today - dt.date.fromisoformat(r["date"])).days < 7]
    total = sum(r["minutes"] for r in this_week)
    target = daily_target * 7
    return round(total / target * 100, 1)

# -------- 운동 추천 (ExerciseDB API) --------
def get_exercises(body_part="legs", limit=3):
    url = "https://exercisedb.dev/api/v1/exercises"
    try:
        res = requests.get(url, params={"bodyPart": body_part})
        data = res.json()
        return data[:limit]
    except Exception:
        return []

# -------- Streamlit UI --------
st.title("🏃‍♂️ 30대 이상 성인 하루 권장 운동량 트래커")

st.sidebar.header("사용자 정보 입력")
name = st.sidebar.text_input("이름", "홍길동")
age = st.sidebar.number_input("나이", 30, 80, 35)
gender = st.sidebar.selectbox("성별", ["남성", "여성"])
weight = st.sidebar.number_input("체중 (kg)", 40, 120, 70)
experience = st.sidebar.selectbox("운동 경험", ["none", "intermediate", "advanced"])

daily_target = recommended_minutes_per_day(age, experience)
st.write(f"✅ {name}님의 하루 권장 운동량: **{daily_target}분**")

# 운동 기록
if "records" not in st.session_state:
    st.session_state["records"] = []

minutes = st.number_input("오늘 운동한 시간 (분)", 0, 180, 30)
if st.button("운동 기록 저장"):
    st.session_state["records"].append({
        "date": str(dt.date.today()),
        "minutes": minutes
    })
    st.success("운동 기록이 저장되었습니다 ✅")

# 달성률 계산
if st.session_state["records"]:
    achievement = calculate_achievement(st.session_state["records"], daily_target)
    st.metric("이번 주 달성률", f"{achievement}%")
else:
    st.info("운동 기록을 입력해주세요.")

# 운동 추천 섹션
st.subheader("💪 추천 운동 (하체 기준)")
for ex in get_exercises("legs"):
    st.write(f"**{ex['name']}** - {ex['target']}")
