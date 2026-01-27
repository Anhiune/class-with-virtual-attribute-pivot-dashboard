import pandas as pd

df = pd.read_excel(r'Course designation form--Cardinal Virtues (Four Pillars Project) - Copy.xlsx')

print("=" * 50)
print("DATAFRAME SHAPE:", df.shape)
print("=" * 50)

print("\nCOLUMNS:")
for i, col in enumerate(df.columns):
    print(f"  {i}: {col[:60]}...")

print("\n" + "=" * 50)
print("FIRST 5 ROWS SAMPLE:")
print("=" * 50)
for col in df.columns:
    print(f"\n--- {col[:40]} ---")
    print(df[col].head(5).tolist())
