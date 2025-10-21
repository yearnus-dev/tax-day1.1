# 납세자 데이터 (이름, 소득)
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

# for문으로 각 납세자 반복 처리
for person in taxpayers:
    tax = calculate_tax(person["income"])
    print(f"{person['name']}의 세금은 {tax:,.0f}원입니다.")
