import streamlit as st
import time
import pandas as pd

# 🎨 페이지 기본 설정
st.set_page_config(page_title="당뇨병 걷기운동 챗봇", page_icon="🚶‍♀️", layout="centered")

# 🧠 세션 초기화
if "step" not in st.session_state:
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
        {"type": "bot", "text": "몇 가지 질문에 답해주시면 맞춤형 걷기운동 권장량을 안내해드릴게요."},
        {"type": "bot", "text": "현재 나이를 입력해주세요. (예: 35)"}
    ]


# 🧩 연령대 구분
def get_age_group(age: int):
    if 30 <= age < 40: return "30대"
    elif 40 <= age < 50: return "40대"
    elif 50 <= age < 60: return "50대"
    elif age >= 60: return "60대 이상"
    else: return None


# 📋 권장사항 데이터
def get_recommendation(age_group):
    data = {
        "30대": {"steps": 10000, "minutes": "30~40", "intensity": "중강도", "details": "빠르게 걷기", "frequency": "주 5회 이상"},
        "40대": {"steps": 10000, "minutes": "30~40", "intensity": "중강도", "details": "대화는 가능하지만 노래는 어려운 속도", "frequency": "주 5회 이상"},
        "50대": {"steps": 9000, "minutes": "25~35", "intensity": "중강도", "details": "편안한 속도로 빠르게 걷기", "frequency": "주 5회 이상"},
        "60대 이상": {"steps": 7500, "minutes": "20~30", "intensity": "저~중강도", "details": "무리하지 않는 범위의 걷기", "frequency": "주 5회 이상"}
    }
    return data.get(age_group, None)


# 💬 메시지 출력
for msg in st.session_state.messages:
    if msg["type"] == "bot":
        st.markdown(f"**🤖 {msg['text']}**")
    else:
        st.markdown(f"<div style='text-align:right;color:#3b82f6;'>🧍‍♂️ {msg['text']}</div>", unsafe_allow_html=True)


# 🧠 챗봇 로직
def chatbot_logic(user_input):
    step = st.session_state.step
    userData = st.session_state.userData
    msgs = st.session_state.messages

    if step == 0:
        try:
            age = int(user_input)
        except ValueError:
            msgs.append({"type": "bot", "text": "숫자로 된 나이를 입력해주세요. (예: 45)"})
            return
        age_group = get_age_group(age)
        if not age_group:
            msgs.append({"type": "bot", "text": "30세 이상의 나이만 지원됩니다."})
            return
        userData["age"] = age
        userData["ageGroup"] = age_group
        msgs.append({"type": "bot", "text": f"{age_group}이시군요. 당뇨병 유형을 선택해주세요."})
        st.session_state.step = 1
        st.session_state.choices = ["1형 당뇨병", "2형 당뇨병"]
        return

    elif step == 1:
        if user_input not in ["1형 당뇨병", "2형 당뇨병"]:
            msgs.append({"type": "bot", "text": "1형 또는 2형 중에서 선택해주세요."})
            return
        userData["diabetesType"] = user_input
        msgs.append({"type": "bot", "text": "현재 평소 활동 수준은 어떠신가요?"})
        st.session_state.step = 2
        st.session_state.choices = ["거의 안함", "가끔 (주 1-2회)", "자주 (주 3-4회)", "매우 자주 (주 5회 이상)"]
        return

    elif step == 2:
        userData["activityLevel"] = user_input
        msgs.append({"type": "bot", "text": "당뇨 합병증(신장, 망막, 신경병증 등)이 있으신가요?"})
        st.session_state.step = 3
        st.session_state.choices = ["없음", "있음"]
        return

    elif step == 3:
        userData["complications"] = user_input
        msgs.append({"type": "bot", "text": "정보를 분석 중입니다... ⏳"})
        st.session_state.step = 4

        # 🧮 결과 계산
        time.sleep(1)
        rec = get_recommendation(userData["ageGroup"])

        msgs.append({"type": "bot", "text": f"📊 {userData['ageGroup']} {userData['diabetesType']} 환자님을 위한 걷기운동 권장사항입니다."})
        time.sleep(0.5)

        # 결과 카드 시각화
        st.subheader("🏃 맞춤 걷기운동 권장사항")
        st.markdown(f"""
        **🦶 하루 걸음 수**: {rec['steps']:,} 걸음  
        **⏱️ 운동 시간**: {rec['minutes']}분  
        **💪 운동 강도**: {rec['intensity']}  
        **📅 빈도**: {rec['frequency']}  
        **✨ 세부사항**: {rec['details']}
        """)

        # ⚠️ 주의사항
        warnings = [
            "• 운동 전후 혈당 측정",
            "• 저혈당 대비 간식 준비",
            "• 편안한 운동화 착용",
            "• 발 상처 여부 확인"
        ]
        if userData["complications"] == "있음":
            warnings += ["• 합병증이 있으므로 담당 의사 상담 필수", "• 처음엔 짧은 시간부터 시작하세요"]
        if userData["activityLevel"] == "거의 안함":
            warnings += ["• 권장량의 50%부터 시작하세요", "• 2~4주에 걸쳐 점진적으로 늘리세요"]

        st.markdown("### ⚠️ 주의사항")
        st.info("\n".join(warnings))

        # 📊 걸음 수 그래프
        st.markdown("### 📈 목표 걸음 수 비교")
        df = pd.DataFrame({
            "카테고리": ["현재 평균(한국 성인)", f"{userData['ageGroup']} 권장"],
            "걸음 수": [5500, rec["steps"]]
        })
        st.bar_chart(df.set_index("카테고리"))

        # 🎯 목표 달성률 게이지
        current = 5500
        progress = min(current / rec["steps"], 1.0)
        st.markdown("### 🚶‍♀️ 현재 걸음 대비 권장량 달성률")
        st.progress(progress)
        st.write(f"현재 약 **{progress*100:.1f}%** 수준입니다.")

        # 💡 팁
        st.markdown("""
        ---
        💡 **운동 팁**  
        • 식후 1~2시간 후 걷기가 혈당 조절에 효과적입니다.  
        • 10분씩 여러 번 나누어 걷기도 좋습니다.  
        • 스마트워치나 만보기 앱으로 기록을 남기세요.
        """)

        # 🔁 다시 시작
        st.session_state.step = 5
        st.session_state.choices = ["새로 시작하기"]
        return

    elif step == 5:
        if user_input == "새로 시작하기":
            st.session_state.clear()
            st.experimental_rerun()
        return


# 🧭 입력 영역
choices = st.session_state.get("choices", None)
user_input = None

if choices:
    user_input = st.radio("선택지를 고르세요 👇", choices, key=f"radio_{st.session_state.step}")
    if st.button("확인"):
        st.session_state.messages.append({"type": "user", "text": user_input})
        chatbot_logic(user_input)
        st.experimental_rerun()
else:
    user_input = st.text_input("✏️ 메시지를 입력하세요", key=f"text_{st.session_state.step}")
    if st.button("보내기"):
        if user_input.strip():
            st.session_state.messages.append({"type": "user", "text": user_input})
            chatbot_logic(user_input)
            st.experimental_rerun()


# 🟡 주의 문구
st.markdown("---")
st.warning("⚠️ 본 챗봇은 일반적인 정보 제공용이며, 의학적 조언을 대체하지 않습니다. 운동 전 반드시 의사와 상담하세요.")
