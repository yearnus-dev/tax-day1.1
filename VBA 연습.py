import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Income & Tax Comparison", layout="wide")
st.title("💰 Income & Tax Comparison App")

uploaded_file = st.file_uploader("📤 엑셀 파일을 업로드하세요 (.xls, .xlsx, .xlsm)", type=["xls", "xlsx", "xlsm"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.subheader("📋 원본 데이터 미리보기")
        st.dataframe(df, use_container_width=True)

        tax_rate = st.slider("세율 (%)", 0, 50, 10)

        if "income" in df.columns:
            df["calculated_tax"] = df["income"] * (tax_rate / 100)
            st.subheader("💵 세금 계산 결과")
            st.dataframe(df[["name", "income", "calculated_tax"]], use_container_width=True)

            st.subheader("📊 인별 소득 및 세금 비교 그래프")
            st.bar_chart(df.set_index("name")[["income", "calculated_tax"]])

            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            st.download_button(
                label="📥 계산된 결과 다운로드 (Excel)",
                data=output.getvalue(),
                file_name="tax_calculated.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("❌ 'income' 열이 존재하지 않습니다. 엑셀 파일을 확인해주세요.")
    except Exception as e:
        st.error(f"파일을 불러오는 중 오류가 발생했습니다: {e}")
else:
    st.info("엑셀 파일을 업로드하면 계산이 시작됩니다.")
