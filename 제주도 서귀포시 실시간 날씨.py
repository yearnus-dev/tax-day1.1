# app.py
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="서귀포 실시간 날씨", page_icon="🌤️", layout="centered")
st.title("🌤️ 제주도 서귀포시 실시간 날씨 (OpenWeatherMap)")

# --- 설정: API 키 불러오기 ---
# 1) Streamlit Cloud 사용 시: st.secrets["OPENWEATHER_API_KEY"]
# 2) 로컬 실행 시: 환경변수로 설정하거나 아래 text_input으로 직접 입력
OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY") if st.secrets else None

if not OPENWEATHER_API_KEY:
    OPENWEATHER_API_KEY = st.text_input(
        "OpenWeatherMap API Key를 입력하세요 (또는 Streamlit Secrets에 설정하세요)",
        type="password"
    )

# --- 서귀포 좌표 (위도, 경도) ---
# 정확한 관측/원하시는 스테이션 좌표로 바꿔도 됩니다.
LAT = 33.26
LON = 126.51

# --- helper: API 호출 ---
def fetch_current_weather(lat, lon, api_key, units="metric", lang="kr"):
    """
    OpenWeatherMap Current Weather API (By coordinates).
    반환: dict (JSON) 또는 None
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units,  # 'metric' => Celsius
        "lang": lang     # 한국어 묘사
    }
    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API 호출 실패: {e}")
        return None

# 버튼으로 새로고침 가능
if st.button("🔄 최신 날씨 받아오기") or "last_fetch" not in st.session_state:
    st.session_state.last_fetch = datetime.utcnow().isoformat()

if OPENWEATHER_API_KEY:
    data = fetch_current_weather(LAT, LON, OPENWEATHER_API_KEY)
    if data:
        # 핵심 정보 파싱
        name = data.get("name", "Seogwipo")
        weather = data["weather"][0] if data.get("weather") else {}
        main = data.get("main", {})
        wind = data.get("wind", {})
        sys = data.get("sys", {})

        desc = weather.get("description", "-")
        icon = weather.get("icon")  # 아이콘 코드 (예: 01d)
        temp = main.get("temp")
        feels_like = main.get("feels_like")
        humidity = main.get("humidity")
        pressure = main.get("pressure")
        wind_speed = wind.get("speed")
        dt = data.get("dt")  # UTC timestamp

        # 화면 출력
        col1, col2 = st.columns([2,1])
        with col1:
            st.subheader(f"{name} 현재 날씨")
            st.write(f"**상태:** {desc}")
            st.write(f"**기온:** {temp} ℃ (체감: {feels_like} ℃)")
            st.write(f"**습도:** {humidity} %")
            st.write(f"**기압:** {pressure} hPa")
            st.write(f"**풍속:** {wind_speed} m/s")
        with col2:
            if icon:
                icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png"
                st.image(icon_url, width=100)
            if dt:
                local_time = datetime.fromtimestamp(dt).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
                st.caption(f"관측 시각: {local_time}")

        # Raw JSON (개발용, 원하면 접기)
        with st.expander("원시 JSON 보기"):
            st.json(data)

        # 참고 및 업데이트 시각
        st.markdown("---")
        st.write("데이터 출처: OpenWeatherMap (현재 날씨 API).")
    else:
        st.warning("날씨 데이터를 불러오지 못했습니다. API 키와 네트워크를 확인하세요.")
else:
    st.info("먼저 OpenWeatherMap API 키를 입력하세요. (https://openweathermap.org 에서 발급)")
