import pandas as pd

df = pd.read_excel(r'Course designation form--Cardinal Virtues (Four Pillars Project) - Copy.xlsx')

print("=" * 50)
print("UNIQUE VALUES IN KEY COLUMNS")
print("=" * 50)

# Cardinal virtues column
virtue_col = [c for c in df.columns if 'Cardinal virtues' in c][0]
print(f"\n--- Cardinal Virtues (unique values) ---")
print(df[virtue_col].unique().tolist())

# Terms column
term_col = [c for c in df.columns if 'Term' in c][0]
print(f"\n--- Terms offered (sample) ---")
print(df[term_col].head(20).tolist())

# Course column
course_col = [c for c in df.columns if 'Course department' in c][0]
print(f"\n--- Course info (sample) ---")
print(df[course_col].head(15).tolist())

print("\n--- All data rows for virtue column ---")
print(df[virtue_col].value_counts())
