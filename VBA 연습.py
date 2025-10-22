import streamlit as st
import pandas as pd

# 🧾 페이지 기본 설정
st.set_page_config(page_title="Income & Tax Comparison", layout="wide")

st.title("💰 Income & Tax Comparison App")

# 🧮 [1] 엑셀 파일 업로드
uploaded_file = st.file_uploader("📤 엑셀 파일을 업로드하세요 (.xls, .xlsx, .xlsm)", type=["xls", "xlsx", "xlsm"])

if uploaded_file:
    # 🧾 [2] 엑셀 데이터 불러오기
    df = pd.read_excel(uploaded_file)

    st.subheader("📋 원본 데이터 미리보기")
    st.dataframe(df, use_container_width=True)

    # 🧮 [3] 세율 입력 (기본값 10%)
    tax_rate = st.slider("세율 (%)", 0, 50, 10)

    # 📈 [4] 세금 계산
    if "income" in df.columns:
        df["calculated_tax"] = df["income"] * (tax_rate / 100)

        st.subheader("💵 세금 계산 결과")
        st.dataframe(df[["name", "income", "calculated_tax"]], use_container_width=True)

        # 📊 [5] 시각화
        st.subheader("📊 인별 소득 및 세금 비교 그래프")
        st.bar_chart(df.set_index("name")[["income", "calculated_tax"]])

        # 📥 [6] 다운로드 버튼
        output = df.to_excel(index=False)
        st.download_button(
            label="📥 계산된 결과 다운로드 (Excel)",
            data=output,
            file_name="tax_calculated.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("❌ 'income' 열이 존재하지 않습니다. 엑셀 파일을 확인해주세요.")
else:
    st.info("엑셀 파일을 업로드하면 계산이 시작됩니다.")

