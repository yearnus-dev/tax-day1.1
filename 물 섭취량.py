# 💧 water_intake_chatbot.py
import streamlit as st
import requests

# ---------------------------
# 🧾 Open API 설정 (API Ninjas Quotes)
# ---------------------------
API_URL = "https://api.api-ninjas.com/v1/quotes?category=health"
API_KEY = "YOUR_API_KEY_HERE"  # 👉 여기에 본인 API 키 입력

# ---------------------------
# 💧 물 섭취량 계산 함수
# ---------------------------
def calculate_water_intake(weight, activity_level):
    """체중과 활동량을 기반으로 하루 권장 물 섭취량(ml)을 계산"""
    base = weight * 30  # 기본: 1kg당 30ml
    if activity_level == "낮음":
        factor = 1.0
    elif activity_level == "보통":
        factor = 1.2
    else:  # 높음
        factor = 1.4
    return round(base * factor, 1)

# ---------------------------
# 🌐 Open API에서 건강 관련 메시지 가져오기
# ---------------------------
def get_health_quote():
    headers = {"X-Api-Key": API_KEY}
    try:
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                quote = data[0]["quote"]
                author = data[0]["author"]
                return f"💬 {quote} — *{author}*"
        return "💡 건강은 매일의 작은 습관에서 시작됩니다!"
    except Exception as e:
        return f"⚠️ API 호출 오류: {e}"

# ---------------------------
# 💬 Streamlit UI 구성
# ---------------------------
st.set_page_config(page_title="하루 물 섭취량 챗봇", page_icon="💧")
st.title("💧 하루 물 섭취량 추천 챗봇")
st.write("나이, 성별, 체중, 활동량을 입력하면 하루 권장 물 섭취량을 알려드릴게요!")

# 사용자 입력
with st.form("user_input_form"):
    name = st.text_input("이름을 입력하세요", value="홍길동")
    age = st.number_input("나이 (세)", min_value=10, max_value=100, value=30)
    gender = st.selectbox("성별", ["남성", "여성"])
    weight = st.number_input("체중 (kg)", min_value=30.0, max_value=150.0, value=60.0)
    activity = st.radio("활동량", ["낮음", "보통", "높음"])
    submitted = st.form_submit_button("추천 받기 💧")

# 결과 출력
if submitted:
    intake_ml = calculate_water_intake(weight, activity)
    intake_l = intake_ml / 1000
    st.success(f"✅ {name}님의 하루 권장 물 섭취량은 약 **{intake_l:.2f}리터** 입니다!")
    st.info(get_health_quote())

# 챗봇 대화 스타일
st.markdown("---")
st.caption("💬 Powered by Streamlit + API Ninjas")
