import pandas as pd
import numpy as np

# --- 1. Generate Synthetic Data ---
print("Generating 1000 rows of synthetic data...")

# Options
depts = ['MATH', 'ENG', 'HIST', 'PHIL', 'THEO', 'BIOS', 'BUS']
virtues = ['Justice', 'Prudence', 'Temperance', 'Fortitude']
terms = ['Fall 2025', 'Spring 2026', 'J-Term 2026', 'Fall 2026', 'Spring 2027', 'Unknown']
ays = {
    'Fall 2025': 'AY 25', 'Spring 2026': 'AY 25', 'J-Term 2026': 'AY 25',
    'Fall 2026': 'AY 26', 'Spring 2027': 'AY 26', 'Unknown': 'Unknown'
}
instructors = ['Prof A', 'Prof B', 'Prof C', 'Prof D', 'Prof E']
delivery_modes = ['Virtual', 'Not marked']

rows = []
for i in range(1000):
    term = np.random.choice(terms)
    dept = np.random.choice(depts)
    rows.append({
        'Source': 'Use Synthetic',
        'Course Code': f"{dept} {np.random.randint(100, 499)}",
        'Department': dept,
        'Instructor name': np.random.choice(instructors),
        'Cardinal virtues addressed': np.random.choice(virtues),
        'Term': term,
        'Academic Year': ays[term],
        'DeliveryMode': np.random.choice(delivery_modes, p=[0.2, 0.8]),
        'Semester': term.split(' ')[0]
    })

df = pd.DataFrame(rows)
print(f"Data Generated. Shape: {df.shape}")
print(df.head(3))
print("-" * 30)

# --- 2. Test Pivot Logic from app.py ---

def test_pivot(name, dataframe, index_col, columns_col, values_col='Course Code', agg='count'):
    print(f"Testing {name}...")
    try:
        pivot = dataframe.pivot_table(
            index=index_col,
            columns=columns_col,
            values=values_col,
            aggfunc=agg,
            fill_value=0
        )
        print(f"  [PASS] Created pivot {pivot.shape}")
        
        # Test Flattening (used for Chart)
        reset = pivot.reset_index()
        melted = reset.melt(id_vars=[reset.columns[0]], var_name='Category', value_name='Count')
        print(f"  [PASS] Melted for chart {melted.shape}")
        
    except Exception as e:
        print(f"  [FAIL] Error: {e}")

# View 3: Overview
test_pivot("Overview: Course Offerings", df[df['Academic Year'].str.startswith('AY')], 'Academic Year', 'Semester')

# View 4: Virtue by Year
test_pivot("Trends: Virtue by Year", df, 'Cardinal virtues addressed', 'Academic Year')

# View 5: Virtue by Semester
test_pivot("Trends: Virtue by Semester", df, 'Cardinal virtues addressed', 'Semester')

# View 6: Instructor Load
# Filter top 20 logic
top_instructors = df['Instructor name'].value_counts().head(20).index
filtered_instr = df[df['Instructor name'].isin(top_instructors)]
test_pivot("Analysis: Instructor Load", filtered_instr, 'Instructor name', 'Cardinal virtues addressed')

# View 7: Department Alignment
test_pivot("Analysis: Department Alignment", df, 'Department', 'Cardinal virtues addressed')

# View 8: Virtual Adoption
test_pivot("Analysis: Virtual Adoption", df, 'Academic Year', 'DeliveryMode')

print("-" * 30)
print("Stress Test Complete.")
