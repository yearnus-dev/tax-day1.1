import csv

def calculate_tax(income):
    """소득의 10%를 세금으로 계산"""
    tax = income * 0.10
    after_tax_income = income - tax
    return tax, after_tax_income

def save_to_csv(income, tax, after_tax_income, filename="tax_result.csv"):
    """결과를 CSV 파일로 저장"""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["소득", "세금", "세후 소득"])
        writer.writerow([income, tax, after_tax_income])
    print(f"결과가 {filename} 파일에 저장되었습니다.")

if __name__ == "__main__":
    income = int(input("소득을 입력하세요 (원): "))
    tax, after_tax_income = calculate_tax(income)
    print(f"예상 세금: {tax:,.0f}원")
    print(f"세후 소득: {after_tax_income:,.0f}원")
    save_to_csv(income, tax, after_tax_income)
