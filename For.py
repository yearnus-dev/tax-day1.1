import streamlit as st

# 제목
st.title("💰 납세자 세금 계산기")

# 납세자 데이터
taxpayers = [
    {"name": "홍길동", "income": 55000000},
    {"name": "김철수", "income": 42000000},
    {"name": "이영희", "income": 72000000}
]

# 세율 계산 함수
def calculate_tax(income):
    if income <= 50000000:
        return income * 0.06  # 6%
    elif income <= 70000000:
        return income * 0.15  # 15%
    else:
        return income * 0.24  # 24%

# 납세자 데이터 표시
st.subheader("📋 납세자 데이터")
st.table(taxpayers)

# 버튼 클릭 시 세금 계산
if st.button("세금 계산하기"):
    st.subheader("💵 계산 결과")
    for person in taxpayers:
        tax = calculate_tax(person["income"])
        st.write(f"**{person['name']}**의 세금은 **{tax:,.0f}원** 입니다.")
