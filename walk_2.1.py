import streamlit as st
from datetime import datetime

st.set_page_config(page_title="당뇨 예방 걷기 챗봇", layout="wide")

# ---------- Helpers ----------

def init_state():
    if 'chat' not in st.session_state:
        st.session_state.chat = []  # list of (role, text)
    if 'profile' not in st.session_state:
        st.session_state.profile = {}


def add_message(role, text):
    st.session_state.chat.append((role, text))


def clamp_age(a):
    try:
        a = int(a)
    except:
        return 30
    return min(max(a, 30), 40)


# Simple personalization algorithm
# Returns (recommended_minutes_per_day, reasoning_text)

def compute_recommendation(age, weight, office_worker, sitting_hours, daily_10min_walk, recent_3day_total):
    # Baseline target (minutes per day)
    base = 30  # evidence-based modest target for cardio prevention

    # Adjust by risk / lifestyle
    adjustment = 0

    if office_worker:
        adjustment += 10
    if sitting_hours >= 8:
        adjustment += 10
    # heavier weight -> suggest more activity
    if weight >= 85:
        adjustment += 10
    elif weight >= 75:
        adjustment += 5

    # If already active, allow lower increase and recommend maintenance
    active_today = daily_10min_walk >= 30
    active_recent = recent_3day_total >= 90

    if active_today and active_recent:
        # maintain but recommend slightly higher for prevention
        recommended = max(base, daily_10min_walk)
        reasoning = (
            f"현재 하루에 10분 이상 걷는 시간이 {daily_10min_walk}분이고, 최근 3일 총 걷기 {recent_3day_total}분으로 활동량이 좋은 편입니다."
            " 유지와 약간의 강화(하루 10~15분 추가)를 권장합니다."
        )
        return recommended, reasoning

    recommended = base + adjustment

    # Cap recommended to reasonable bounds
    recommended = int(min(max(recommended, 25), 75))

    reasoning_parts = []
    reasoning_parts.append(f"기본 권장: {base}분/일")
    if office_worker:
        reasoning_parts.append("직장인(주로 앉아 있음): +10분")
    if sitting_hours >= 8:
        reasoning_parts.append(f"하루 앉아있는 시간 {sitting_hours}시간: +10분")
    if weight >= 85:
        reasoning_parts.append(f"체중 {weight}kg: +10분 (체중 높을수록 활동 권장)")
    elif weight >= 75:
        reasoning_parts.append(f"체중 {weight}kg: +5분")

    reasoning = "; ".join(reasoning_parts) + f" → 권장: {recommended}분/일"

    return recommended, reasoning


# ---------- UI ----------

init_state()

st.title("🩺 당뇨병 예방을 위한 걷기 운동 챗봇 (30–40대 남성 대상)")
st.markdown(
    "이 챗봇은 사용자의 생활정보를 바탕으로 **개인화된 하루 권장 걷기시간**과 실천 팁을 제공합니다. \n주의: 의료적 진단이나 처방이 아닙니다. 필요시 전문가와 상담하세요."
)

# Layout: left - input form, right - chat history
col1, col2 = st.columns([1, 1.6])

with col1:
    st.header("프로필 입력")
    with st.form("profile_form"):
        age = st.number_input("나이", value=35, min_value=30, max_value=40, step=1)
        weight = st.number_input("체중(kg)", value=75, min_value=40)
        office_worker = st.checkbox("직장인(주로 앉아서 일함)")
        sitting_hours = st.slider("하루 중 앉아있는 시간(시간)", 0, 16, 8)

        st.markdown("---")
        st.subheader("활동 입력 (최근/평상시)")
        daily_10min_walk = st.number_input("평상시 하루 동안 10분 이상 걷는 시간(분)", value=20, min_value=0)
        recent_3day_total = st.number_input("최근 3일 걷기 총시간(분)", value=45, min_value=0)

        submitted = st.form_submit_button("권장 걷기량 계산")

    if submitted:
        age = clamp_age(age)
        st.session_state.profile = {
            'age': age,
            'weight': weight,
            'office_worker': office_worker,
            'sitting_hours': sitting_hours,
            'daily_10min_walk': daily_10min_walk,
            'recent_3day_total': recent_3day_total,
            'updated_at': datetime.now().isoformat()
        }

        recommended, reasoning = compute_recommendation(
            age, weight, office_worker, sitting_hours, daily_10min_walk, recent_3day_total
        )

        # Build assistant reply
        reply = []
        reply.append(f"안녕하세요 — 입력 감사합니다. (나이: {age}세, 체중: {weight}kg)")
        reply.append(reasoning)
        reply.append(f"추천 목표: **{recommended}분/일** 걷기 (중등도 이상, 보통 '빨리 걷기' 수준).")

        # If user is far below target, give progressive plan
        current = daily_10min_walk
        if current < recommended:
            diff = recommended - current
            # Suggest stepwise plan
            if diff <= 10:
                plan = f"현재와 비교해 하루에 추가로 {diff}분만 더 걷는 것을 목표로 하세요."
            else:
                plan = (
                    f"하루에 추가로 {diff}분이 필요합니다. 처음 2주간은 하루 +10분씩 늘리고, 그 다음 주에 목표량에 도달하도록 점진적으로 올리세요."
                )
            reply.append(plan)
        else:
            reply.append("현재 활동량이 권장량 수준이거나 그 이상입니다. 유지와 꾸준한 실천을 권장합니다.")

        # Provide actionable tips
        tips = []
        tips.append("매 시간 최소 5분 정도 일어나서 걷기(좌식 시간 줄이기)")
        tips.append("점심시간 10~20분 빠르게 걷기 추가")
        tips.append("주말에는 긴 걷기(한 번에 40~60분)를 1회 이상 시도")
        tips.append("걷기 강도를 높이면 같은 시간에 더 큰 효과를 얻습니다(빠른 걸음).")

        reply.append("실천 팁:\n- " + "\n- ".join(tips))

        add_message('user', '프로필 입력 및 권장 계산 요청')
        add_message('assistant', "\n\n".join(reply))

with col2:
    st.header("대화형 창")

    # Show chat history
    if len(st.session_state.chat) == 0:
        add_message('assistant', '안녕하세요! 오른쪽에서 프로필과 활동을 입력하고 "권장 걷기량 계산"을 눌러주세요. 질문이 있으면 아래 입력창에 자유롭게 적어주세요.')

    for role, text in st.session_state.chat:
        if role == 'user':
            st.markdown(f"**사용자:** {text}")
        else:
            st.markdown(f"**챗봇:** {text}")
        st.markdown("---")

    # Follow-up question box
    st.subheader("질문 또는 상태 업데이트")
    with st.form("follow_up_form"):
        user_msg = st.text_area("메시지 입력 (예: 오늘 20분 걸었어요, 어떻게 더 늘릴까요?)", value="")
        follow_sub = st.form_submit_button("전송")

    if follow_sub and user_msg.strip():
        # Simple handling of a couple common follow-ups
        add_message('user', user_msg)

        # Basic parser for minutes reported
        import re
        m = re.search(r"(\d{1,3})\s*분", user_msg)
        if m:
            minutes = int(m.group(1))
            # update recent_3day_total conservatively
            profile = st.session_state.get('profile', {})
            if profile:
                # roll recent total: assume new day replaces oldest -> simple model
                new_total = min(profile.get('recent_3day_total', 0) + minutes, 300)
                profile['recent_3day_total'] = new_total
                profile['daily_10min_walk'] = minutes
                st.session_state.profile = profile
                recommended, reasoning = compute_recommendation(
                    profile['age'], profile['weight'], profile['office_worker'], profile['sitting_hours'], profile['daily_10min_walk'], profile['recent_3day_total']
                )
                resp = f"오늘 보고하신 걷기 {minutes}분을 반영했습니다. 최신 권장: {recommended}분/일.\n{reasoning}"
            else:
                resp = "프로필이 없어서 활동만 기록했습니다. 먼저 프로필을 입력해 주세요."
        else:
            # if user asks a question, give a generic helpful response
            q = user_msg.lower()
            if '증가' in q or '늘리' in q:
                resp = (
                    "걷기 시간을 늘리고 싶다면 '짧고 자주' 전략이 효과적입니다. 예: 하루 3회 10분 걷기→ 점차 15분씩 늘리기, 매시간 5분 걷기."
                )
            elif '강도' in q or '속도' in q:
                resp = (
                    "강도를 올리려면 평소보다 숨이 약간 찰 정도의 빠른 걸음을 목표로 하세요(말은 할 수 있으나 노래는 못함). 인터벌(빠르게 1분-느리게 2분)도 도움이 됩니다."
                )
            else:
                resp = "좋은 질문입니다 — 구체적으로 알고 싶은 점(예: 주간 계획, 식이 연동, 워밍업 등)을 적어주시면 더 자세히 답해드릴게요."

        add_message('assistant', resp)


st.markdown("\n---\n")
st.caption("데이터는 사용자가 입력한 값에 따라 계산됩니다. 의료적 판단은 전문가 상담을 따르세요.")

# EOF
