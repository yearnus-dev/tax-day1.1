import streamlit as st
import csv
import os

# 세금 계산 함수
def calculate_tax(income):
    """소득의 10%를 세금으로 계산"""
    return income * 0.1

# CSV 파일 저장 함수
def save_to_csv(taxpayer):
    filename = "tax_results.csv"
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "income", "tax"])
        # 파일이 처음 생성될 때 헤더 추가
        if not file_exists:
            writer.writeheader()
        writer.writerow(taxpayer)

# Streamlit 앱
st.title("💬 납세자 세금 계산 챗봇")

st.write("안녕하세요! 납세자 정보를 입력하면 세금을 계산해드릴게요 😊")

# 사용자 입력
name = st.text_input("납세자 이름을 입력하세요:")
income = st.number_input("소득을 입력하세요 (원)", min_value=0.0, step=100000.0)

# 버튼 클릭 시 처리
if st.button("세금 계산하기"):
    if not name:
        st.warning("이름을 입력해주세요.")
    elif income <= 0:
        st.warning("소득은 0보다 커야 합니다.")
    else:
        tax = calculate_tax(income)
        st.success(f"💰 {name}님의 세금은 **{tax:,.0f}원** 입니다!")

        # CSV 저장
        taxpayer = {"name": name, "income": income, "tax": tax}
        save_to_csv(taxpayer)
        st.info("✅ 세금 계산 결과가 CSV 파일(tax_results.csv)에 저장되었습니다.")

# 저장된 데이터 확인
if st.checkbox("저장된 납세자 목록 보기"):
    if os.path.exists("tax_results.csv"):
        st.subheader("📄 저장된 세금 계산 내역")
        st.dataframe(
            st.experimental_data_editor(
                st.session_state.get("tax_data", None)
            )
            if "tax_data" in st.session_state
            else st.dataframe(st.data_editor)
        )

        with open("tax_results.csv", "r", encoding="utf-8") as f:
            st.download_button(
                "📥 CSV 파일 다운로드",
                data=f,
                file_name="tax_results.csv",
                mime="text/csv"
            )
    else:
        st.info("아직 저장된 납세자 데이터가 없습니다.")
