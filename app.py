import streamlit as st
import pandas as pd
import data_processor
import altair as alt

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Cardinal Virtues Dashboard", layout="wide")

# Custom CSS for the "White Box" (Table) and "Mint Box" (Chart) theme
# Custom CSS for the "White Box" (Table) and "Mint Box" (Chart) theme
st.markdown("""
<style>
    /* Main Background - Force light theme colors */
    .stApp {
        background-color: #F5F7F8;
        color: #333333; /* Default text color */
    }
    
    /* Import Section Style */
    .import-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 50px;
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        max-width: 800px;
        margin: auto;
        text-align: center;
        /* Force dark text inside this white box */
        color: #2c3e50 !important;
    }
    
    /* Force headers/text inside import container to be dark */
    .import-container h1, .import-container p, .import-container div {
        color: #2c3e50 !important;
    }
    
    /* 
       CSS :has() selector strategy to style the parent Streamlit container 
       wrapping the widgets. 
    */
    
    /* White Box Column */
    div[data-testid="stVerticalBlock"]:has(div.white-box-marker) {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #EAEAEA;
        /* Force Text Color */
        color: #333333 !important;
    }

    /* Mint Box Column */
    div[data-testid="stVerticalBlock"]:has(div.mint-box-marker) {
        background-color: #E0F7FA;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #B2EBF2;
        /* Force Text Color */
        color: #006064 !important;
    }
    
    /* Force standard headers to be dark everywhere */
    h1, h2, h3, p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] {
        color: #333333 !important;
    }
    
    /* Markers (Hidden) */
    .white-box-marker, .mint-box-marker {
        display: none;
    }
    
    /* Helper text */
    .sub-text {
        font-size: 0.9em;
        color: #666 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data(file):
    return data_processor.process_file(file)

# --- HELPER FUNCTIONS ---
# --- HELPER FUNCTIONS ---
def show_split_view(dataframe, index_col, columns_col, title_pivot="Pivot Table", title_chart="Visualization", values_col='Course Code', agg='count'):
    """
    Renders the split view: Left = White Box (Pivot), Right = Mint Box (Chart)
    """
    col1, col2 = st.columns([5, 4], gap="medium")
    
    # 1. Prepare Data
    pivot = dataframe.pivot_table(
        index=index_col,
        columns=columns_col,
        values=values_col,
        aggfunc=agg,
        fill_value=0
    )
    # Add Total for table display
    pivot_display = pivot.copy()
    pivot_display['Total'] = pivot_display.sum(axis=1)

    # 2. Render Left Column (White Box)
    with col1:
        # Marker for CSS targeting
        st.markdown('<div class="white-box-marker"></div>', unsafe_allow_html=True)
        st.markdown(f'<h3>{title_pivot}</h3>', unsafe_allow_html=True)
        st.dataframe(pivot_display, use_container_width=True, height=500)

    # 3. Render Right Column (Mint Box)
    with col2:
        # Marker for CSS targeting
        st.markdown('<div class="mint-box-marker"></div>', unsafe_allow_html=True)
        
        # Header + Chart Toggle in columns
        c_head_1, c_head_2 = st.columns([2, 1])
        with c_head_1:
            st.markdown(f'<h3>{title_chart}</h3>', unsafe_allow_html=True)
        with c_head_2:
            chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Area", "Heatmap"], key=title_chart, label_visibility="collapsed")

        # Move chart down for cleaner look
        st.markdown("<br>", unsafe_allow_html=True)

        # Chart Data Preparation
        reset = pivot.reset_index()
        melted = reset.melt(id_vars=[reset.columns[0]], var_name='Category', value_name='Count')
        
        primary_dim = reset.columns[0] # e.g., Academic Year
        secondary_dim = 'Category'      # e.g., Semester/Virtue
        
        # Custom Color Scale: Purple, Light Green, Gray shades
        custom_colors = alt.Scale(range=['#9b59b6', '#2ecc71', '#95a5a6', '#8e44ad', '#27ae60', '#7f8c8d'])
        
        # Chart Logic
        if chart_type == "Bar":
            # Grouped Bar Chart (Cleaner, Single Axis, No Overflow)
            chart = alt.Chart(melted).mark_bar().encode(
                x=alt.X(primary_dim, title=index_col, axis=alt.Axis(labelAngle=0)),
                y=alt.Y('Count', title='Count'),
                xOffset=alt.XOffset(secondary_dim),
                color=alt.Color(secondary_dim, title=columns_col, scale=custom_colors),
                tooltip=[primary_dim, secondary_dim, 'Count']
            ).properties(
                height=500 # Strict match to table
            ).interactive()

        elif chart_type == "Line":
            chart = alt.Chart(melted).mark_line(point=True).encode(
                x=alt.X(primary_dim, title=index_col),
                y=alt.Y('Count', title='Count'),
                color=alt.Color(secondary_dim, title=columns_col, scale=custom_colors),
                tooltip=[primary_dim, secondary_dim, 'Count']
            ).properties(height=500).interactive()

        elif chart_type == "Area":
            chart = alt.Chart(melted).mark_area(opacity=0.6).encode(
                x=alt.X(primary_dim, title=index_col),
                y=alt.Y('Count', title='Count', stack=None),
                color=alt.Color(secondary_dim, title=columns_col, scale=custom_colors),
                tooltip=[primary_dim, secondary_dim, 'Count']
            ).properties(height=500).interactive()
            
        elif chart_type == "Heatmap":
            chart = alt.Chart(melted).mark_rect().encode(
                x=alt.X(primary_dim, title=index_col),
                y=alt.Y(secondary_dim, title=columns_col),
                color=alt.Color('Count', title='Count'),
                tooltip=[primary_dim, secondary_dim, 'Count']
            ).properties(height=500).interactive()

        st.altair_chart(chart, use_container_width=True)

# --- APP STATE MANAGEMENT ---
if 'df' not in st.session_state:
    st.session_state.df = None
if 'active_page' not in st.session_state:
    st.session_state.active_page = "Landing"

def reset_app():
    st.session_state.df = None
    st.session_state.active_page = "Landing"

# --- SIDEBAR LOGIC ---
# Conditionally render sidebar content
if st.session_state.df is None:
    # HIDE SIDEBAR CSS when on Landing
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # SHOW SIDEBAR CONTENT
    with st.sidebar:
        st.title("Navigation")
        
        if st.button("📤 Upload New File", use_container_width=True):
            reset_app()
            st.rerun()
            
        st.markdown("---")
        
        st.header("Datasets & Audits")
        mode_dataset = st.radio(
            "Select Dataset View:",
            [
                "Audit: Raw Form Export",
                "Dataset: Master Course List"
            ],
            index=None,
            key="nav_dataset"
        )
        
        st.header("Analysis & Insights")
        mode_analysis = st.radio(
            "Select Analysis:",
            [
                "Overview: Course Offerings",
                "Trends: Virtue by Year",
                "Trends: Virtue by Semester",
                "Analysis: Instructor Load",
                "Analysis: Department Alignment",
                "Analysis: Virtual Adoption"
            ],
            index=None,
            key="nav_analysis"
        )
        
        st.header("Tools & Catalogs")
        mode_tools = st.radio(
            "Select Tool:",
            [
                "Tool: Course Lookup",
                "Catalog: Virtual Courses"
            ],
            index=None,
            key="nav_tools"
        )
        
        st.header("Quality Assurance")
        mode_quality = st.radio(
            "Select Quality Check:",
            [
                "Quality: Issues Log",
                "Quality: Tag Validation"
            ],
            index=None,
            key="nav_quality"
        )

        # Determine Active Page
        if mode_analysis: st.session_state.active_page = mode_analysis
        elif mode_tools: st.session_state.active_page = mode_tools
        elif mode_quality: st.session_state.active_page = mode_quality
        elif mode_dataset: st.session_state.active_page = mode_dataset


# --- MAIN CONTENT ---

if st.session_state.df is None:
    # --- LANDING / IMPORT STATE ---
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div class="import-container">
            <h1>Import dataset for pivot tables or insight</h1>
            <p class="sub-text">Please upload your Course Designation Form (Excel) to begin analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Uploader explicitly here
        uploaded_file = st.file_uploader("Choose a file", type=['xlsx'], label_visibility="collapsed")
        
        if uploaded_file is not None:
            try:
                with st.spinner("Processing Data..."):
                    df = load_data(uploaded_file)
                    st.session_state.df = df
                    st.session_state.active_page = "Overview: Course Offerings" # Default landing
                    st.rerun()
            except Exception as e:
                st.error(f"Error processing file: {e}")

else:
    # --- DASHBOARD STATE ---
    df = st.session_state.df
    active_page = st.session_state.active_page
    
    # Handle case where page is still landing but we have data
    if active_page == "Landing":
        active_page = "Overview: Course Offerings"

    st.title(active_page)

    # 1. Audit: Raw Form Export
    if active_page == "Audit: Raw Form Export":
        st.markdown('<div class="pivot-box">', unsafe_allow_html=True)
        st.write("Original Data Source (Form Responses)")
        st.dataframe(df[df['Source'] == 'Form'], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


    # 2. Dataset: Master Course List
    elif active_page == "Dataset: Master Course List":
        st.markdown('<div class="pivot-box">', unsafe_allow_html=True)
        st.write("Full Processed Dataset (Normalized)")
        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Overview: Course Offerings
    elif active_page == "Overview: Course Offerings":
        valid_ay = df[df['Academic Year'].str.startswith('AY')]
        show_split_view(valid_ay, 'Academic Year', 'Semester', 
                       title_pivot="Course Count by Year/Sem", title_chart="Trend Overview")

    # 4. Trends: Virtue by Year
    elif active_page == "Trends: Virtue by Year":
        show_split_view(df, 'Cardinal virtues addressed', 'Academic Year',
                       title_pivot="Virtue Distribution (Year)", title_chart="Virtue Trends")

    # 5. Trends: Virtue by Semester
    elif active_page == "Trends: Virtue by Semester":
        show_split_view(df, 'Cardinal virtues addressed', 'Semester',
                       title_pivot="Virtue Distribution (Semester)", title_chart="Seasonality Analysis")

    # 6. Analysis: Instructor Load
    elif active_page == "Analysis: Instructor Load":
         # Top 20 for readability
        top_instructors = df['Instructor name'].value_counts().head(20).index
        filtered = df[df['Instructor name'].isin(top_instructors)]
        show_split_view(filtered, 'Instructor name', 'Cardinal virtues addressed',
                       title_pivot="Instructor Focus Area", title_chart="Instructor Load Visualization")

    # 7. Analysis: Department Alignment
    elif active_page == "Analysis: Department Alignment":
        show_split_view(df, 'Department', 'Cardinal virtues addressed',
                       title_pivot="Departmental Breakdown", title_chart="Department Strategy")

    # 8. Analysis: Virtual Adoption
    elif active_page == "Analysis: Virtual Adoption":
        show_split_view(df, 'Academic Year', 'DeliveryMode',
                       title_pivot="Virtual Penetration", title_chart="Adoption Rate")

    # 9. Tool: Course Lookup
    elif active_page == "Tool: Course Lookup":
        st.markdown('<div class="pivot-box">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: sel_virtue = st.multiselect("Virtue", df['Cardinal virtues addressed'].unique())
        with col2: sel_ay = st.multiselect("Academic Year", df['Academic Year'].unique())
        with col3: sel_dept = st.multiselect("Department", df['Department'].unique())
        
        filtered_df = df.copy()
        if sel_virtue: filtered_df = filtered_df[filtered_df['Cardinal virtues addressed'].isin(sel_virtue)]
        if sel_ay: filtered_df = filtered_df[filtered_df['Academic Year'].isin(sel_ay)]
        if sel_dept: filtered_df = filtered_df[filtered_df['Department'].isin(sel_dept)]
        
        st.dataframe(filtered_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 10. Catalog: Virtual Courses
    elif active_page == "Catalog: Virtual Courses":
        st.markdown('<div class="pivot-box">', unsafe_allow_html=True)
        virt_df = df[df['DeliveryMode'] == 'Virtual']
        if len(virt_df) == 0:
            st.warning("No courses explicitly marked as 'Virtual' were found.")
        else:
            st.dataframe(virt_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 11. Quality: Issues Log
    elif active_page == "Quality: Issues Log":
        st.markdown('<div class="pivot-box">', unsafe_allow_html=True)
        unknowns = df[(df['Department'] == 'Unknown') | (df['Term'] == 'Unknown')]
        st.write(f"Found {len(unknowns)} potential data quality issues.")
        st.dataframe(unknowns, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 12. Quality: Tag Validation
    elif active_page == "Quality: Tag Validation":
        st.markdown('<div class="pivot-box">', unsafe_allow_html=True)
        st.subheader("Virtue / Tag Analysis")
        vc = df['Cardinal virtues addressed'].value_counts()
        st.dataframe(vc, use_container_width=True)
        st.info("Expected: Justice, Prudence, Temperance, Fortitude")
        st.markdown('</div>', unsafe_allow_html=True)

