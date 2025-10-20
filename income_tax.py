import streamlit as st

st.title("💰 소득세 계산기")
st.write("입력한 소득에 따라 예상 세금과 소득 수준을 계산합니다.")

# 사용자 입력
income = st.number_input("소득을 입력하세요 (단위: 원)", min_value=0, step=1000000, value=55000000)

# 세금 계산
if income <= 12000000:
    level = "저소득층"
    tax_rate = 0.06
elif income <= 46000000:
    level = "중간소득층"
    tax_rate = 0.15
elif income <= 88000000:
    level = "고소득층"
    tax_rate = 0.24
else:
    level = "초고소득층"
    tax_rate = 0.35

tax = income * tax_rate

# 결과 표시
st.subheader("📊 계산 결과")
st.write(f"**소득 수준:** {level}")
st.write(f"**소득 금액:** {income:,.0f} 원")
st.write(f"**예상 세금:** {tax:,.0f} 원")

# 시각화 (선택사항)
import pandas as pd

df = pd.DataFrame({
    "항목": ["세후 금액", "세금"],
    "금액": [income - tax, tax]
})
st.bar_chart(df.set_index("항목"))
