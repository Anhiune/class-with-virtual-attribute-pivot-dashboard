import pandas as pd

df = pd.read_excel(r'Course designation form--Cardinal Virtues (Four Pillars Project) - Copy.xlsx')

print("Searching for 'Virtual' in all columns...")
found = False
for col in df.columns:
    # Convert to string, ensure case insensitive check
    matches = df[df[col].astype(str).str.contains("Virtual", case=False, na=False)]
    if not matches.empty:
        found = True
        print(f"\nFOUND 'Virtual' IN COLUMN: {col}")
        print(f"Sample values:")
        print(matches[col].unique().tolist()[:10])

if not found:
    print("\n'Virtual' keyword NOT found in any cell.")
    print("Checking for 'VIRT' just in case (as mentioned in prompt 'VIRT [Pillar 1]')...")
    for col in df.columns:
        matches = df[df[col].astype(str).str.contains("VIRT", case=False, na=False)]
        if not matches.empty:
            print(f"\nFOUND 'VIRT' IN COLUMN: {col}")
