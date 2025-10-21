import streamlit as st
import csv
import io

st.set_page_config(page_title="간단한 소득세 계산기", page_icon="💰")
st.title("💰 소득의 10% 세금 계산기")
st.write("입력한 소득의 10%를 세금으로 계산하고, 결과를 CSV로 저장합니다.")

# -------------------------------
# 세금 계산 함수
# -------------------------------
def calculate_tax(income):
    """소득의 10%를 세금으로 계산"""
    tax = income * 0.10
    after_tax_income = income - tax
    return tax, after_tax_income

# -------------------------------
# CSV 저장 함수 (Streamlit용)
# -------------------------------
def create_csv(income, tax, after_tax_income):
    """CSV 데이터를 메모리에 생성"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["소득", "세금", "세후 소득"])
    writer.writerow([income, tax, after_tax_income])
    return output.getvalue().encode("utf-8")

# -------------------------------
# 사용자 입력
# -------------------------------
income = st.number_input("📥 소득을 입력하세요 (단위: 원)", min_value=0, step=1000000, value=55000000)

# -------------------------------
# 계산 및 출력
# -------------------------------
if income > 0:
    tax, after_tax_income = calculate_tax(income)

    st.subheader("📊 계산 결과")
    st.write(f"**소득:** {income:,.0f} 원")
    st.write(f"**세금 (10%):** {tax:,.0f} 원")
    st.write(f"**세후 소득:** {after_tax_income:,.0f} 원")

    # CSV 생성
    csv_data = create_csv(income, tax, after_tax_income)

    # 다운로드 버튼
    st.download_button(
        label="📂 계산 결과 CSV 다운로드",
        data=csv_data,
        file_name="tax_result.csv",
        mime="text/csv"
    )
else:
    st.info("소득을 입력하면 결과가 표시됩니다.")
