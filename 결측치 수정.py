import pandas as pd

data = {
    "name": ["홍길동", "김철수", "이영희", "박민수"],
    "income": [55000000, 42000000, None, 60000000],
    "age": [35.0, None, 45.0, 50.0]
}

df = pd.DataFrame(data)
print("📊 원본 데이터:")
print(df)

# 결측치 확인
print("\n🔍 결측치 개수:")
print(df.isnull().sum())

# 결측치를 평균값으로 채우기
df['income'].fillna(df['income'].mean(), inplace=True)
df['age'].fillna(df['age'].mean(), inplace=True)

print("\n✅ 결측치 채운 후:")
print(df)
