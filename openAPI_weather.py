# 🧭 [1] 라이브러리 불러오기
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# 🗺️ [2] 기본 설정
st.set_page_config(page_title="서귀포시 날씨 예측", page_icon="🌤️", layout="centered")

st.title("🌤️ 서귀포시 날씨 예측 대시보드")
st.markdown("**Open-Meteo API**를 이용해 실시간 날씨와 향후 예보를 제공합니다.")

# 🧩 [3] API 요청 함수 정의
def get_weather_data(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Asia/Seoul"
    }
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

# 📍 [4] 서귀포시 좌표
latitude = 33.2530
longitude = 126.5618

# 🌦️ [5] 데이터 가져오기
data = get_weather_data(latitude, longitude)

if data:
    # 🌡️ 현재 시간
    now = datetime.now().strftime("%Y-%m-%dT%H:00")

    # 시간별 데이터
    hourly = pd.DataFrame(data["hourly"])
    hourly["time"] = pd.to_datetime(hourly["time"])
    current_temp = hourly.loc[hourly["time"] == now, "temperature_2m"]

    if not current_temp.empty:
        st.metric("현재 서귀포시 기온", f"{current_temp.values[0]:.1f} °C")
    else:
        st.warning("현재 기온 정보를 불러올 수 없습니다.")

    # 📅 일별 데이터
    daily = pd.DataFrame(data["daily"])
    daily["time"] = pd.to_datetime(daily["time"])
    daily = daily.rename(columns={
        "temperature_2m_max": "최고기온(°C)",
        "temperature_2m_min": "최저기온(°C)",
        "precipitation_sum": "강수량(mm)"
    })

    st.subheader("📅 향후 7일 예보")
    st.dataframe(daily)

    # 📈 그래프 시각화
    st.subheader("🌡️ 일별 최고·최저기온 변화")
    fig, ax = plt.subplots()
    ax.plot(daily["time"], daily["최고기온(°C)"], label="최고기온", marker="o")
    ax.plot(daily["time"], daily["최저기온(°C)"], label="최저기온", marker="o")
    ax.set_xlabel("날짜")
    ax.set_ylabel("기온 (°C)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("🌧️ 일별 강수량 변화")
    fig2, ax2 = plt.subplots()
    ax2.bar(daily["time"], daily["강수량(mm)"], color="skyblue")
    ax2.set_xlabel("날짜")
    ax2.set_ylabel("강수량 (mm)")
    st.pyplot(fig2)

else:
    st.error("날씨 데이터를 불러오지 못했습니다. 인터넷 연결을 확인하세요.")
