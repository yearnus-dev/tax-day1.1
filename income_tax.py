# 소득수준
income = 55000000  # 소득 (단위: 원)
tax = 0
if income <= 12000000:
    level = "저소득층"
    tax = income * 0.06
elif income <= 46000000:
    level = "중간소득층"
    tax = income * 0.15
elif income <= 88000000:
    level = "고소득층"
    tax = income * 0.24
else:
    level = "초고소득층"
    tax = income * 0.35
print(f"소득 수준: {level}")
print(f"소득 금액: {income:,}원")
print(f"예상 세금: {tax:,.0f}원")
