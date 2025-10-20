import streamlit as st
import pandas as pd

# -------------------------------
# 제목 및 설명
# -------------------------------
st.set_page_config(page_title="종합소득세 계산기", page_icon="💰")
st.title("💰 종합소득세 계산기")
st.write("""
이 앱은 **소득 구간별 누진세율**에 따라 예상 종합소득세를 계산합니다.  
2024년 기준 대한민국 소득세율을 기준으로 합니다.
""")

# -------------------------------
# 세율표 설정
# -------------------------------
TAX_BRACKETS = [
    {"limit": 12000000, "rate": 0.06},
    {"limit": 46000000, "rate": 0.15},
    {"limit": 88000000, "rate": 0.24},
    {"limit": 150000000, "rate": 0.35},
    {"limit": 300000000, "rate": 0.38},
    {"limit": 500000000, "rate": 0.40},
    {"limit": 1000000000, "rate": 0.42},
    {"limit": float("inf"), "rate": 0.45},
]

# -------------------------------
# 사용자 입력
# -------------------------------
income = st.number_input("📥 연 소득을 입력하세요 (단위: 원)", min_value=0, step=1000000, value=55000000)

# -------------------------------
# 세금 계산 함수
# -------------------------------
def calc_tax(income):
    tax = 0
    prev_limit = 0
    details = []

    for bracket in TAX_BRACKETS:
        limit = bracket["limit"]
        rate = bracket["rate"]

        if income > limit:
            taxable = limit - prev_limit
        else:
            taxable = max(0, income - prev_limit)

        tax_segment = taxable * rate
        tax += tax_segment
        details.append({
            "과세표준": f"{prev_limit+1:,.0f} ~ {limit:,.0f}",
            "세율": f"{rate*100:.0f}%",
            "과세금액": f"{taxable:,.0f} 원",
            "세금": f"{tax_segment:,.0f} 원"
        })

        if income <= limit:
            break
        prev_limit = limit

    return tax, details

# -------------------------------
# 계산 및 출력
# -------------------------------
if income > 0:
    total_tax, details = calc_tax(income)
    st.subheader("📊 세금 계산 결과")
    st.write(f"**총 예상 세금:** {total_tax:,.0f} 원")
    st.write(f"**세후 소득:** {income - total_tax:,.0f} 원")

    st.markdown("---")
    st.subheader("📋 구간별 세금 상세 내역")
    st.dataframe(pd.DataFrame(details))

    # 그래프 표시
    chart_data = pd.DataFrame({
        "항목": ["세후 소득", "세금"],
        "금액": [income - total_tax, total_tax]
    })
    st.bar_chart(chart_data.set_index("항목"))
else:
    st.info("소득을 입력하면 계산 결과가 표시됩니다.")

# -------------------------------
# 출처
# -------------------------------
st.markdown("""
---
📘 **참고:**  
- 국세청 종합소득세율표 (2024년 기준)  
- 본 계산기는 실제 세액과 다를 수 있으며 참고용입니다.
""")
