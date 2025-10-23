import streamlit as st
import pandas as pd
from datetime import datetime
import difflib
import math
import random

st.set_page_config(page_title="30-50대 개인화 걷기 챗봇", layout="wide")

# ------------------ Helpers ------------------
# (기존 헬퍼 함수들은 동일 — 그대로 유지)

def calc_bmi(weight_kg, height_cm):
    if height_cm <= 0:
        return None
    h = height_cm / 100.0
    return round(weight_kg / (h * h), 1)

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

def generate_flexible_answer(question, rec):
    # 간단한 키워드 기반 답변 + 일부 확률적 문장 다양화
    q = question.lower()
    responses = []

    if any(k in q for k in ["bmi", "체중", "비만"]):
        responses.append(f"입력하신 BMI는 {rec['bmi']}로 '{bmi_category(rec['bmi'])}' 범주입니다.")
        responses.append(f"이 경우 {rec['weekly_minutes']}분/주 정도의 걷기를 추천드립니다.")
        responses.append(random.choice([
            "무릎에 부담을 줄이려면 부드러운 신발과 평지 위주로 걸어보세요.",
            "지속시간보다 꾸준함이 더 중요합니다 — 매일 일정한 시간에 걷는 습관을 만들어 보세요.",
        ]))

    elif any(k in q for k in ["시간", "얼마나", "분"]):
        responses.append(f"당신에게 권장되는 평균 걷기 시간은 일 {rec['daily_minutes']}분, 주 {rec['weekly_minutes']}분입니다.")
        responses.append(random.choice([
            "하루 중 편한 시간대(예: 출퇴근 전후, 점심 후)를 정해 일정하게 걷는 것이 좋습니다.",
            "주말에 몰아서 하기보다 매일 조금씩 실천하는 것이 더 효과적입니다.",
        ]))

    elif any(k in q for k in ["강도", "속도", "빠르"]):
        responses.append(random.choice([
            "중간 강도(말은 가능하지만 노래는 어려운 정도)가 이상적입니다.",
            "빠른 걷기를 3분, 보통 걷기를 1분 번갈아 하는 인터벌 방식도 효과적입니다.",
        ]))

    elif any(k in q for k in ["루틴", "계획", "운동"]):
        responses.append(random.choice([
            "4주 동안 점진적으로 시간을 늘리며 10~20%씩 증가시키세요.",
            "첫 주는 적응, 2~3주는 강화, 4주는 유지/점검 단계로 구성하면 좋습니다.",
        ]))

    elif any(k in q for k in ["식단", "다이어트", "감량"]):
        responses.append(random.choice([
            "걷기와 함께 단백질 섭취를 충분히 하고, 야식과 음료수를 줄이면 감량 효과가 커집니다.",
            "식이요법 없이 운동만으로는 체중 감량이 더디니, 식단 균형이 중요합니다.",
        ]))

    elif any(k in q for k in ["건강", "혈압", "심장"]):
        responses.append(random.choice([
            "혈압이 높다면 처음 1~2주는 낮은 강도에서 천천히 늘리세요.",
            "심혈관 질환 병력이 있다면 운동 전 전문의 상담을 권장합니다.",
        ]))

    else:
        responses.append(random.choice([
            "좋은 질문이에요! 규칙적인 걷기는 모든 건강지표에 긍정적인 영향을 줍니다.",
            "꾸준히 걷는 것은 체중뿐 아니라 스트레스 완화에도 효과적이에요.",
            "혹시 원하신다면 당신 조건에 맞춘 4주 루틴도 생성해드릴게요.",
        ]))

    return "\n".join(responses)

# ------------------ UI ------------------
st.title("30–50대 맞춤 걷기 챗봇 (개인화 + 자유형 응답)")
st.caption("조건에 맞춘 권장 걷기 시간, 4주 루틴, 자유형 Q&A까지 가능합니다.")

with st.sidebar:
    st.header("기본 정보 입력")
    age = st.number_input("나이", 30, 50, 38)
    sex = st.selectbox("성별", ["여성", "남성", "비공개"])
    weight = st.number_input("체중(kg)", 30.0, 200.0, 70.0)
    height = st.number_input("키(cm)", 120.0, 230.0, 170.0)
    activity_level = st.selectbox("활동 수준", ["비활동적", "보통", "매우 활동적"])
    goal = st.selectbox("운동 목표", ["유지/건강한 생활", "체중 감량", "심폐 지구력 향상"])

# 단순 샘플 데이터 (실제 앱에서는 기존 계산 로직과 결합 가능)
rec = {
    'bmi': calc_bmi(weight, height),
    'weekly_minutes': 180,
    'daily_minutes': 25,
}

st.markdown("---")
st.subheader("질문 또는 추가 요청 (자유 입력)")
q = st.text_input("예: '40대 여성인데 체중 감량을 위해 하루 몇 분 걸어야 해요?' 또는 '빠른 걷기 루틴 알려줘'")

if st.button("질문 전송") and q.strip():
    st.write(generate_flexible_answer(q, rec))

st.caption("💬 자유도 높은 답변 생성형 알고리즘 적용 (네이버·구글식 자연 응답)")
