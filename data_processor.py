import pandas as pd
import re
import numpy as np

# --- CONFIGURATION ---
AY_MAPPING = {
    'Fall 2025': 'AY 25',
    'J-Term 2026': 'AY 25',
    'Spring 2026': 'AY 25',
    'Summer 2026': 'AY 25',
    
    'Fall 2026': 'AY 26',
    'J-Term 2027': 'AY 26',
    'Spring 2027': 'AY 26',
    'Summer 2027': 'AY 26',
    
    'Fall 2027': 'AY 27',
    'Spring 2027': 'AY 26', # Duplicate, handled by AY 26 logic above
    # Add more as needed or use logic
    # User rule: "Fall 2025 is mapped to AY 25 not add to 26"
}

VIRTUES = ['Justice', 'Prudence', 'Temperance', 'Fortitude']

# --- HARDCODED DATA INJECTION ---
# "Justice and Prudence EDUC210 Fall and Spring, usually taught by Muffet Trout"
# "Justice and Fortitude EDUC 329 Fall and Spring, usually taught by Chelda Smith"
# "Fortitude: EDUC 370... all in fall"
# "Fortitude: EDUC 330/332 normally fall and spring. But not fall 2026."

def get_hardcoded_courses():
    rows = []
    
    # helper
    def add(dept, num, title, virt_str, term_list, instr, virtual=False):
        for term, ay in term_list:
            rows.append({
                'Course Code': f"{dept} {num}",
                'Department': dept,
                'Course Number': num,
                'Course Title': title,
                'Section': 'All',
                'Instructor name': instr,
                'Cardinal virtues addressed': virt_str,
                'Term': term,
                'Academic Year': ay,
                'DeliveryMode': 'Virtual' if virtual else 'Not marked',
                'Hardcoded': True
            })

    # EDUC 210
    terms_210 = [('Fall 2025', 'AY 25'), ('Spring 2026', 'AY 25'), ('Fall 2026', 'AY 26'), ('Spring 2027', 'AY 26')]
    add('EDUC', '210', 'Introduction to Education', 'Justice;Prudence', terms_210, 'Muffet Trout')

    # EDUC 329
    terms_329 = [('Fall 2025', 'AY 25'), ('Spring 2026', 'AY 25'), ('Fall 2026', 'AY 26'), ('Spring 2027', 'AY 26')]
    add('EDUC', '329', 'Equitable Schools', 'Justice;Fortitude', terms_329, 'Chelda Smith')

    # Fortitude Group: 370, 371, 372, 373, 316, 317, 318, 319, 380 (All in Fall)
    fort_courses = [
        ('370', 'Kaback'), ('371', 'D. Monson'), ('372', 'M. Trout'), ('373', 'M. Trout'),
        ('316', 'E. Gullickson'), ('317', 'E. Gullickson'), ('318', 'TBD'), ('319', 'TBD'), ('380', 'TBD')
    ]
    terms_fall_only = [('Fall 2025', 'AY 25'), ('Fall 2026', 'AY 26')]
    for num, instr in fort_courses:
        add('EDUC', num, 'Fortitude Special', 'Fortitude', terms_fall_only, instr)

    # EDUC 330/332: Fall and Spring normally. BUT NOT Fall 2026.
    # J-Term 2027 is Study Abroad.
    # Terms: Fall 2025 (Yes), Spring 2026 (Yes), Fall 2026 (NO), Spring 2027 (Yes), J-Term 2027 (Yes)
    terms_330 = [('Fall 2025', 'AY 25'), ('Spring 2026', 'AY 25'), ('Spring 2027', 'AY 26'), ('J-Term 2027', 'AY 26')]
    add('EDUC', '330', 'Clinical Practice', 'Fortitude', terms_330, 'Muffet Trout')
    add('EDUC', '332', 'Clinical Practice II', 'Fortitude', terms_330, 'Muffet Trout')

    return pd.DataFrame(rows)

# --- PARSING FUNCTIONS ---

def normalize_virtues(val):
    if not isinstance(val, str): return []
    val = val.replace(';', ',')
    found = []
    for v in VIRTUES:
        if v.lower() in val.lower():
            found.append(v)
    return found

def get_virtual_status(row):
    # Check 'Cardinal virtues' column and 'Term' column for "Virtual"
    # Also user said "Virtual feature... added for all classes"? 
    # But explicitly asked for "VirtualOnly" view.
    # We will search for 'Virtual' string.
    
    text_search = str(row.get('Cardinal virtues addressed', '')) + " " + str(row.get('Term(s) offered', ''))
    if 'virtual' in text_search.lower():
        return 'Virtual'
    return 'Not marked'

def parse_terms(min_year=2025, max_year=2027):
    # Logic to translate "Every Semester" etc.
    # Returns list of dicts: {'Term': 'Fall 2025', 'Academic Year': 'AY 25', 'Semester': 'Fall'}
    
    def expand(text):
        if not isinstance(text, str): return []
        text = text.lower()
        
        results = []
        
        # Explicit mentions
        # Regex for Season + Year (e.g. Fall 2025, Spring 26)
        matches = re.findall(r'(fall|spring|summer|j-term)\s*(\d{4}|\d{2})', text)
        for season, year in matches:
            if len(year) == 2: year = '20' + year
            term_str = f"{season.title()} {year}"
            
            # Map valid ones
            if term_str in AY_MAPPING:
                results.append((term_str, AY_MAPPING[term_str]))
            elif '2025' in term_str and 'fall' in season: # Fall 2025 -> AY 25 explicit hook if missed
                 results.append((term_str, 'AY 25'))
        
        # "Every Semester" / "Each Term" logic
        if 'every' in text or 'each' in text or 'all' in text:
            # Generate defaults for the window
            # Limit to AY 25 and AY 26 for now as requested range
            defaults = [
                ('Fall 2025', 'AY 25'),
                ('Spring 2026', 'AY 25'),
                ('Fall 2026', 'AY 26'),
                ('Spring 2027', 'AY 26')
            ]
            # If specific seasons mentioned? e.g. "Every Fall"
            if 'fall' in text and 'spring' not in text:
                defaults = [x for x in defaults if 'Fall' in x[0]]
            elif 'spring' in text and 'fall' not in text:
                defaults = [x for x in defaults if 'Spring' in x[0]]
                
            # Avoid dupes if regex found them too
            existing_terms = {r[0] for r in results}
            for d in defaults:
                if d[0] not in existing_terms:
                    results.append(d)
                    
        return results

    return expand

def process_file(uploaded_file):
    # Load
    df = pd.read_excel(uploaded_file)
    
    # Rename columns to standard keys
    # Map based on keyword search
    col_map = {}
    for c in df.columns:
        if 'Start' in c: col_map[c] = 'Start'
        elif 'Instructor' in c: col_map[c] = 'Instructor name'
        elif 'Course department' in c: col_map[c] = 'Course Info'
        elif 'Term' in c: col_map[c] = 'Term(s) offered'
        elif 'virtues' in c: col_map[c] = 'Cardinal virtues addressed'
    
    df = df.rename(columns=col_map)
    
    # Pre-cleaning
    processed_rows = []
    term_expander = parse_terms()
    
    # 1. Process FORM Entries
    for idx, row in df.iterrows():
        # Parsing Logic
        raw_course = str(row.get('Course Info', ''))
        raw_term = str(row.get('Term(s) offered', ''))
        virtue_str = str(row.get('Cardinal virtues addressed', ''))
        instructor = str(row.get('Instructor name', ''))
        
        # Virtues
        virtues = normalize_virtues(virtue_str)
        if not virtues: continue # Skip if no virtue? Or keep as 'None'? Keep as 'None' for audit? 
        # User wants pivot by Virtue, so maybe explode virtues too.
        
        # Virtual check
        delivery = get_virtual_status(row)
        
        # Terms
        terms = term_expander(raw_term)
        if not terms:
            terms = [('Unknown', 'Unknown')]
            
        # Course Code Extraction (Simple Regex)
        # Look for "DEPT 123"
        course_match = re.search(r'([A-Z]{3,4})\s*-?(\d{3})', raw_course)
        if course_match:
            dept = course_match.group(1)
            num = course_match.group(2)
            code = f"{dept} {num}"
        else:
            dept = 'Unknown'
            num = 'Unknown'
            code = raw_course[:20] + '...'
            
        # Explode time!
        # Multi-level explode: Terms x Virtues
        for v in virtues:
            for term_name, ay in terms:
                processed_rows.append({
                    'Source': 'Form',
                    'Course Code': code,
                    'Department': dept,
                    'Course Number': num,
                    'Course Title': raw_course, # Keep full string as title for now
                    'Section': 'See Info',
                    'Instructor name': instructor,
                    'Cardinal virtues addressed': v, # Single virtue per row
                    'Term': term_name,
                    'Academic Year': ay,
                    'DeliveryMode': delivery,
                    'Semester': term_name.split(' ')[0] if ' ' in term_name else term_name,
                    'Hardcoded': False
                })

    # 2. Inject Hardcoded
    hard_df = get_hardcoded_courses()
    # Normalize hardcoded to match schema
    for idx, row in hard_df.iterrows():
        virtues = row['Cardinal virtues addressed'].split(';')
        for v in virtues:
            processed_rows.append({
                'Source': 'Hardcoded',
                'Course Code': row['Course Code'],
                'Department': row['Department'],
                'Course Number': row['Course Number'],
                'Course Title': row['Course Title'],
                'Section': row['Section'],
                'Instructor name': row['Instructor name'],
                'Cardinal virtues addressed': v,
                'Term': row['Term'],
                'Academic Year': row['Academic Year'],
                'DeliveryMode': row['DeliveryMode'],
                'Semester': row['Term'].split(' ')[0],
                'Hardcoded': True
            })

    # Final DataFrame
    master_df = pd.DataFrame(processed_rows)
    return master_df

if __name__ == "__main__":
    # Test run
    try:
        df = process_file(r'c:\Users\hoang\Class_Attributes_Data\Course designation form--Cardinal Virtues (Four Pillars Project) - Copy.xlsx')
        print(f"Success! Generated {len(df)} rows.")
        print(df.head())
        df.to_csv('debug_master_data.csv', index=False)
    except Exception as e:
        print(f"Error: {e}")
