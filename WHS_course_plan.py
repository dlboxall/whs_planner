import streamlit as st
import pandas as pd
import ast
from layout import department_sidebar
import base64

#Connect to Dept Codes in sidebar
dept_code_to_name = {
    "BUS": "Business",
    "CSC": "Computer Science",
    "CTE": "CTE",
    "ENG": "English",
    "MUS": ["Fine Arts", "Vocal Music"],
    "MTH": "Mathematics",
    "DRM": "Performing Arts",
    "PED": "Physical Education",
    "SCI": "Science",
    "SOC": "Social Studies",
    "ART": "Visual Arts",
    "WLG": "World Languages"
}
st.set_page_config(page_title="Course Planner", layout="wide")

if "show_intro" not in st.session_state:
    st.session_state.show_intro = True

if st.session_state.show_intro:
    with st.expander("How to Use This Course Planner (Click to Collapse)", expanded=True):
        st.markdown("""
<h3 style='margin-bottom: 0.5em;'>Welcome to the WHS Graduation Planner!</h3>
<p>Use this tool to plan your 4-year high school course pathway and track graduation eligibility.</p>

<h4 style='text-decoration: underline;'>Graduation Requirements Checker</h4>
<p>After selecting courses, scroll to the <strong>Graduation Pathway</strong> dropdown to choose:</p>
<ul>
  <li>🎓 <em>University/Regents-ready</em></li>
  <li>🛠️ <em>Career & Technical Education (CTE)</em></li>
  <li>🏅 <em>Advanced/Honors Endorsement</em></li>
</ul>
<p>The sidebar will show whether you’ve met required credits in each subject for the selected pathway.</p>

<h4 style='text-decoration: underline;'>Department Codes List</h4>
<p>Each elective course requires a 3-letter <strong>Department Code</strong> (e.g., <strong>ART</strong>, <strong>CTE</strong>, <strong>SCI</strong>) before you can choose a course.</p>
<p>Click the <strong>“Department Code”</strong> sidebar dropdown menu to view the full list of codes and their departments.</p>

<h4 style='text-decoration: underline;'>Core & Elective Course Selection</h4>
<p>Each grade level includes:</p>
<ul>
  <li>4 core courses (English, Math, Science, Social Studies)</li>
  <li>4 additional elective courses — shown in rows labeled <strong>Course 5 to Course 8</strong></li>
</ul>

<h4 style='text-decoration: underline;'>Prerequisite Enforcement</h4>
<p>Some advanced courses (like <strong>Chemistry</strong> or <strong>Algebra II</strong>) will only be available if you’ve already added the required prerequisite courses earlier in the planner.</p>

<hr style="margin-top: 1.5em;">

<p><strong>Enjoy planning!</strong> Make sure to scroll and double-check each grade’s section before reviewing graduation progress.</p>
        """, unsafe_allow_html=True)

        if st.button("✅ Close Instructions"):
            st.session_state.show_intro = False

if st.button("📘 Show How-To Guide Again"):
    st.session_state.show_intro = True

# Load and encode Banner.png
with open("Banner.png", "rb") as f:
    data = f.read()
    encoded = base64.b64encode(data).decode()

# Insert base64 image into clickable <img> tag
st.markdown(
    f"""
    <a href="https://www.watertown.k12.sd.us/o/high-school" target="_blank" title="Visit Watertown High School">
        <img src="data:image/png;base64,{encoded}" alt="WHS Banner" style="width: 100%; height: auto;">
    </a>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Two-column layout for student name and pathway selection
name_col, path_col = st.columns(2)

with name_col:
    st.markdown("### Course plan created for:")
    student_name = st.text_input("Enter student name", key="student_name")

with path_col:
    st.markdown("### Please select graduation pathway")
    st.radio(
        label="",
        options=["University", "Career & Technical", "Honors/Scholarship Opportunity"],
        key="grad_pathway"
    )


# Load course catalog
def load_course_catalog():
    df = pd.read_csv("WHS_course_catalog.csv")
    df["Grade Levels"] = df["Grade Levels"].apply(lambda x: ast.literal_eval(str(x)))
    df["Prerequisites"] = df["Prerequisites"].fillna("None")
    df["Tags"] = df["Tags"].fillna("")
    df["Notes"] = df["Notes"].fillna("")
    return df

course_catalog = load_course_catalog()

# Set up grade levels and labels
years = ["9th Grade", "10th Grade", "11th Grade", "12th Grade"]
row_labels_fall = ["English", "Mathematics", "Science", "Social Studies"]
row_labels_spring = ["Course 5", "Course 6", "Course 7", "Course 8"]

# Grade-level guidance messages for hover tooltips
grade_requirements = {
    "9th Grade": "English 9, Algebra I, Speech or Debate, World Geography, Biology, PE/Health [6 credits min]",
    "10th Grade": "English 10, Geometry, World History, Physical Science or Chemistry [6 credits min]",
    "11th Grade": "English 11, Algebra II, US History, Science, Personal Finance(BUS) or Economics(SOC) [6 credits min]",
    "12th Grade": "English 12, US Government, Personal Finance(BUS) or Economics(SOC) [6 credits min]"
}

def hover_year_msg(year):
    msg = grade_requirements.get(year, "No specific requirements listed.")
    return f"""
    <style>
    .tooltip-container {{
        position: relative;
        display: inline-block;
        cursor: help;
    }}

    .tooltip-container .tooltip-text {{
        visibility: hidden;
        width: 280px;
        background-color: #f9f9f9;
        color: #333;
        text-align: left;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        top: 125%;
        left: 0;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        font-size: 0.85rem;
    }}

    .tooltip-container:hover .tooltip-text {{
        visibility: visible;
    }}
    </style>

    <div class="tooltip-container">
        <span style="font-size: 1.5em; font-weight: 600;">{year}</span>
        <div class="tooltip-text">
            Required: {msg}
        </div>
    </div>
    """

# Session state initialization
if "course_plan" not in st.session_state:
    st.session_state.course_plan = {year: ["" for _ in range(8)] for year in years}
    st.session_state.course_plan_codes = {year: ["" for _ in range(8)] for year in years}

if "ms_credits" not in st.session_state:
    st.session_state.ms_credits = ["" for _ in range(4)]

# Middle School Credits
st.header("High School Credit Earned in Middle School")
ms_courses = course_catalog[course_catalog["Grade Levels"].apply(lambda x: 8 in x)]
ms_options = [""] + ms_courses["Course Name"].tolist()
ms_lookup = dict(zip(ms_courses["Course Name"], ms_courses["Course Code"].astype(str)))
ms_cols = st.columns(4)
for i in range(4):
    with ms_cols[i]:
        st.session_state.ms_credits[i] = st.selectbox(
            f"Middle School Course {i+1}",
            ms_options,
            index=ms_options.index(st.session_state.ms_credits[i]) if st.session_state.ms_credits[i] in ms_options else 0,
            key=f"ms_course_{i}"
        )

# Build course prerequisite dictionary
prereq_dict = dict(zip(course_catalog["Course Code"].astype(str), course_catalog["Prerequisites"]))

# Helper to check if prerequisites are met
def has_prereq_met(course_code, current_year, course_plan_codes, prereq_dict, current_index):
    taken = [ms_lookup.get(name, "") for name in st.session_state.ms_credits if name]
    for yr in years:
        for idx, code in enumerate(course_plan_codes[yr]):
            if yr == current_year and idx >= current_index:
                break
            if code:
                taken.append(code)
        if yr == current_year:
            break
    raw = prereq_dict.get(course_code, "None")
    if raw == "None":
        return True
    try:
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, int) or isinstance(parsed, str):
            return str(parsed) in taken
        elif isinstance(parsed, list) and all(isinstance(x, list) for x in parsed):
            return all(any(str(code) in taken for code in group) for group in parsed)
        elif isinstance(parsed, list):
            return any(str(code) in taken for code in parsed)
        else:
            return False
    except:
        return False

english_course_codes_by_grade = {
    "9th Grade": ["2401", "2404"],
    "10th Grade": ["2501", "2504"],
    "11th Grade": ["2601", "2608"],
    "12th Grade": ["2715", "2606"]
}


# Main planner loop
for year in years:
    #st.header(year)
    st.markdown(hover_year_msg(year), unsafe_allow_html=True)

    cols = st.columns(4)
    grade_num = int(year.split()[0].replace("th", "").replace("st", "").replace("nd", "").replace("rd", ""))
    base_courses = course_catalog[course_catalog["Grade Levels"].apply(lambda x: grade_num in x)]

    for i in range(8):
        department = row_labels_fall[i] if i < 4 else row_labels_spring[i - 4]
        col = cols[i % 4]

        with col:
            label = f"{year} – {department}"
            dept_courses = base_courses[base_courses["Department"] == department]

            if i < 4:
                # --- Core subjects ---
                if department == "English":
                    allowed_codes = english_course_codes_by_grade.get(year, [])
                    eligible_courses = dept_courses[
                        dept_courses["Course Code"].astype(str).isin(allowed_codes)
                    ]
                else:
                    eligible_courses = dept_courses[
                        dept_courses["Course Code"].astype(str).apply(
                            lambda code: has_prereq_met(code, year, st.session_state.course_plan_codes, prereq_dict, i)
                        )
                    ]

                if not eligible_courses.empty:
                    options = [""] + eligible_courses["Course Name"].tolist()
                    code_lookup = dict(zip(eligible_courses["Course Name"], eligible_courses["Course Code"].astype(str)))
                    notes_lookup = dict(zip(eligible_courses["Course Name"], eligible_courses["Notes"]))

                    selected_course = st.selectbox(
                        label=label,
                        options=options,
                        index=options.index(st.session_state.course_plan[year][i]) if st.session_state.course_plan[year][i] in options else 0,
                        key=f"{year}_{i}"
                    )

                    st.session_state.course_plan[year][i] = selected_course
                    st.session_state.course_plan_codes[year][i] = code_lookup.get(selected_course, "")

                    if selected_course:
                        note = notes_lookup.get(selected_course, "")
                        if note:
                            st.caption(f"ℹ️ {note}")
                else:
                    st.info(f"No eligible courses found for {department} in {year}.")

            else:
                # --- Electives: 3-letter department code input ---
                course_code_key = f"{year}_{i}_code"

                if course_code_key not in st.session_state:
                    st.session_state[course_code_key] = ""

                st.text_input(
                    f"Enter 3-letter code for Course {i+1}",
                    max_chars=3,
                    key=course_code_key
                )

                course_code = st.session_state[course_code_key].strip().upper()
                department_names = dept_code_to_name.get(course_code, [])

                if isinstance(department_names, str):
                    department_names = [department_names]

                if department_names:
                    dept_courses = base_courses[base_courses["Department"].isin(department_names)]
                    eligible_courses = dept_courses[dept_courses["Course Code"].astype(str).apply(
                        lambda code: has_prereq_met(code, year, st.session_state.course_plan_codes, prereq_dict, i)
                    )]
                else:
                    eligible_courses = pd.DataFrame(columns=base_courses.columns)

                if not eligible_courses.empty:
                    options = [""] + eligible_courses["Course Name"].tolist()
                    code_lookup = dict(zip(eligible_courses["Course Name"], eligible_courses["Course Code"].astype(str)))
                    notes_lookup = dict(zip(eligible_courses["Course Name"], eligible_courses["Notes"]))

                    selected_course = st.selectbox(
                        label=f"{label} – Select Course",
                        options=options,
                        index=options.index(st.session_state.course_plan[year][i]) if st.session_state.course_plan[year][i] in options else 0,
                        key=f"{year}_{i}"
                    )

                    st.session_state.course_plan[year][i] = selected_course
                    st.session_state.course_plan_codes[year][i] = code_lookup.get(selected_course, "")

                    if selected_course:
                        note = notes_lookup.get(selected_course, "")
                        if note:
                            st.caption(f"ℹ️ {note}")
                elif course_code:
                    if not department_names:
                        st.warning(f"'{course_code}' is not a valid department code.")
                    else:
                        st.warning(f"No eligible course found for code '{course_code}' in {year} Grade.")

    st.markdown("---")

# --- DUPLICATE COURSE CODE CHECK GLOBALS ---
unlimited_repeatable_codes = {"1201", "1210", "1221"}  # e.g., Band, Orchestra
limited_repeatable_counts = {"2410": 2}  # e.g., Exp in Reading (max 2 times)

from collections import Counter

def check_for_duplicate_courses(selected_df):
    """Checks for course codes that appear more often than allowed."""
    all_selected_codes = []

    for course_name in st.session_state.ms_credits:
        if course_name:
            row = course_catalog[course_catalog["Course Name"] == course_name]
            if not row.empty:
                all_selected_codes.append(str(row["Course Code"].values[0]))

    for year in st.session_state.course_plan:
        for course_name in st.session_state.course_plan[year]:
            if course_name:
                row = course_catalog[course_catalog["Course Name"] == course_name]
                if not row.empty:
                    all_selected_codes.append(str(row["Course Code"].values[0]))

    code_counts = Counter(all_selected_codes)

    non_repeatable_violations = [
        code for code, count in code_counts.items()
        if (
            (code in unlimited_repeatable_codes and count > 1000)  # safeguard: should never warn
            or (code in limited_repeatable_counts and count > limited_repeatable_counts[code])
            or (code not in unlimited_repeatable_codes and code not in limited_repeatable_counts and count > 1)
        )
    ]
    
    # Report violations in a single summary message
    if non_repeatable_violations:
        names = [
            course_catalog[course_catalog["Course Code"].astype(str) == code]["Course Name"].values[0]
            for code in non_repeatable_violations
            if not course_catalog[course_catalog["Course Code"].astype(str) == code].empty
        ]
        st.error(f"⚠️ Duplicate course selection: {', '.join(names)} — most courses may only be taken once.")

# === PRINT-FRIENDLY VIEW TOGGLE ===

if "print_mode" not in st.session_state:
    st.session_state.print_mode = False

st.markdown("---")
if st.session_state.print_mode:
    if st.button("🔙 Back to Planner"):
        st.session_state.print_mode = False
else:
    if st.button("🖨️ Print-Friendly View"):
        st.session_state.print_mode = True

# === DISPLAY PRINT-FRIENDLY VIEW IF TOGGLED ===
if st.session_state.print_mode:
    import streamlit.components.v1 as components

    # Build raw HTML string directly — no json.dumps or string escaping
    html_printable = f"""<!DOCTYPE html>
<html>
<head>
    <title>{st.session_state.get('student_name', 'Student')}'s 4-Year Plan</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 30px; }}
        h2 {{ text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
    </style>
</head>
<body>
    <h2>{st.session_state.get('student_name', 'Student')}'s 4-Year Course Plan</h2>
    <table>
        <thead><tr><th>Grade</th><th>Core</th><th>Elective</th></tr></thead>
        <tbody>
"""

    for year in years:
        core = ", ".join([c for c in st.session_state.course_plan[year][:4] if c])
        elective = ", ".join([c for c in st.session_state.course_plan[year][4:] if c])
        html_printable += f"<tr><td>{year}</td><td>{core}</td><td>{elective}</td></tr>"

    html_printable += f"""
        </tbody>
        </table>
    
        <div style="margin-top: 24px; display: flex; justify-content: space-between; font-weight: bold;">
            <div>Graduation pathway: {st.session_state.get('grad_pathway', 'Not selected')}</div>
            <div>Total credits: {total_credits}</div>
        </div>
    
        <script>
            window.onload = function() {{
                window.print();
            }};
        </script>
    </body>
    </html>
    """

    # Use iframe to open a real print preview
    components.html(f"""
        <button onclick="const printWindow = window.open('', '_blank');
                         printWindow.document.write(`{html_printable}`);
                         printWindow.document.close();">
            🖨️ Print This Plan
        </button>
    """, height=100)


#----------END PRINT LOOP-------------

def show_graduation_tracker():
    #st.markdown("### 🎓 Graduation Tracker")
    graduation_df = course_catalog.copy()
    selected_df_rows = []
    claimed_courses = set()

    cte_cluster_map = {
        "Ag, Food & Natural Resources": {"9601", "9605", "18102", "18203", "18501"},
        "Architecture & Construction": {"17003", "17004", "17007", "17008"},
        "Business and Finance": {"9115", "9110", "9120"},
        "Education & Training": {"19051", "19052", "19151"},
        "Health Science": {"3066", "3067", "14001", "14002", "14154"},
        "Hospitality & Tourism": {"16052", "16058", "16059", "19253"},
        "Human Services": {"19001", "19051", "19052"},
        "Information Technology": {"5105", "5606", "5700"},
        "Manufacturing": {"13203", "13204", "13207", "13208"},
        "STEM": {"21017", "21018", "21023"},
        "Transportation & Distribution": {"20104", "20110"}
    }

    for course_name in st.session_state.ms_credits + sum(st.session_state.course_plan.values(), []):
        if not course_name:
            continue
        row = graduation_df[graduation_df["Course Name"] == course_name]
        if not row.empty:
            selected_df_rows.append(row)
    selected_df = pd.concat(selected_df_rows, ignore_index=True) if selected_df_rows else pd.DataFrame(columns=graduation_df.columns)

    selected_codes = selected_df["Course Code"].astype(str).tolist()

    selected_pathway = st.session_state.get("grad_pathway", "University")
#----------------------------------------------------------------------------------------------------------------------------------------
#        UNIVERSITY GRADUATION PATHWAY TRACKER
#----------------------------------------------------------------------------------------------------------------------------------------
    if st.session_state.grad_pathway == "University":
        st.subheader("🎓 University Graduation Requirements")
    
        # selected_df = build_selected_df()
        selected_df["Course Code"] = selected_df["Course Code"].astype(str)
        selected_df["Credits"] = pd.to_numeric(selected_df["Credits"], errors="coerce")
        selected_df.dropna(subset=["Credits"], inplace=True)
        check_for_duplicate_courses(selected_df)

        #selected_df["Credits"] = selected_df["Credits"].astype(float)
    
        total_credits = selected_df["Credits"].sum()
        st.markdown(f"**Total Credits:** {total_credits} / 24 required")
    
        # ---- ENGLISH CHECK ----
        required_english_groups = [["2401", "2404"], ["2501", "2504"], ["2601", "2608"], ["2715", "2606"]]
        speech_debate_codes = ["2201", "2205"]
    
        eng_df = selected_df[selected_df["Department"] == "English"]
        valid_english_codes = [code for group in required_english_groups for code in group]
    
        english_grad_df = eng_df[eng_df["Course Code"].isin(valid_english_codes)]
        speech_df = eng_df[eng_df["Course Code"].isin(speech_debate_codes)]
    
        english_credits = english_grad_df["Credits"].sum()
        speech_credits = speech_df["Credits"].sum()
    
        english_met = all(any(code in selected_df["Course Code"].tolist() for code in group) for group in required_english_groups)
    
        if english_credits >= 4 and english_met:
            st.success(f"English: ✅ {english_credits}/4 (group requirements met)")
        else:
            st.warning(f"English: {english_credits}/4 credits — group coverage {'✓' if english_met else '✗'}")
    
        if speech_credits >= 0.5:
            st.success(f"Speech/Debate: ✅ {speech_credits}/0.5")
        else:
            st.warning(f"Speech/Debate: {speech_credits}/0.5")
    
        # ---- MATH CHECK ----
        math_df = selected_df[selected_df["Department"] == "Mathematics"]
        math_credits = math_df["Credits"].sum()
    
        if math_credits >= 3:
            st.success(f"Mathematics: ✅ {math_credits}/3")
        else:
            st.warning(f"Mathematics: {math_credits}/3 (check coverage)")
    
        # ---- SCIENCE CHECK ----
        science_df = selected_df[selected_df["Department"] == "Science"]
        science_credits = science_df["Credits"].sum()
    
        if science_credits >= 3:
            st.success(f"Science: ✅ {science_credits}/3")
        else:
            st.warning(f"Science: {science_credits}/3 (check coverage)")
    
        # ---- SOCIAL STUDIES CHECK ----
        ss_df = selected_df[selected_df["Department"] == "Social Studies"]
        ss_credits = ss_df["Credits"].sum()
        ss_codes = ss_df["Course Code"].tolist()
    
        ss_required = {
            "Geography": ["8101"],
            "World History": ["8201"],
            "U.S. History": ["8304","8310"],
            "U.S. Government": ["8401","8405"]
        }
        ss_met = all(any(code in ss_codes for code in group) for group in ss_required.values())
    
        if ss_credits >= 3 and ss_met:
            st.success(f"Social Studies: ✅ {ss_credits}/3 (required classes met)")
        else:
            st.warning(f"Social Studies: {ss_credits}/3 (check required coverage)")
        claimed_courses.update(ss_df["Course Code"])
    
        # --- Finance (8701) or Personal Finance (9120) ---
        finance_codes = ["8701", "9120"]
        finance_df = selected_df[selected_df["Course Code"].isin(finance_codes)]
        finance_credits = finance_df["Credits"].sum()
        if finance_credits >= 0.5:
            st.success(f"Econ/Finance: ✅ {finance_credits}/0.5")
        else:
            st.warning(f"Econ/Finance: {finance_credits}/0.5")
        claimed_courses.update(finance_df["Course Code"])

        # ---- Native American Studies ----
        na_studies_df = selected_df[selected_df["Course Code"].astype(str) == "8410"]
        na_credits = na_studies_df["Credits"].sum()
        
        if na_credits >= 0.5:
            st.success(f"Native American Studies: ✅ {na_credits}/0.5")
        else:
            st.warning(f"Native American Studies: {na_credits}/0.5")
    
        # --- PE/Health ---
        pe_df = selected_df[
            (selected_df["Department"] == "Physical Education") &
            (selected_df["Course Name"] != "Health Education")
        ]

        pe_credits = pe_df["Credits"].sum()
        health_df = selected_df[selected_df["Course Name"].str.contains("Health", case=False, na=False)]
        health_credits = health_df["Credits"].sum()
    
        if pe_credits >= 0.5 and health_credits >= 0.5:
            st.success(f"PE/Health: ✅ PE {pe_credits}, Health {health_credits} (1.0 total)")
        else:
            st.warning(f"PE/Health: PE {pe_credits}, Health {health_credits} (1.0 total)")
        claimed_courses.update(pe_df["Course Code"])
        claimed_courses.update(health_df["Course Code"])
    
        # --- Fine Arts ---
        fine_df = selected_df[
            selected_df["Department"].isin([
                "Fine Arts", "Vocal Music", "Performing Arts", "Visual Arts"
            ])
        ]        
        
        fine_credits = fine_df["Credits"].sum()
        if fine_credits >= 1:
            st.success(f"Fine Arts: ✅ {fine_credits}/1.0")
        else:
            st.warning(f"Fine Arts: {fine_credits}/1.0")
        claimed_courses.update(fine_df["Course Code"])
    
        # ---- WORLD LANGUAGE CHECK ----
        wl_df = selected_df[selected_df["Department"] == "World Languages"]
        wl_codes = wl_df["Course Code"].tolist()
        wl_credits = wl_df["Credits"].sum()
    
        same_lang_met = False
        if len(wl_codes) >= 2:
            from collections import Counter
            counts = Counter([code[:2] for code in wl_codes])
            same_lang_met = any(v >= 2 for v in counts.values())
    
        if wl_credits >= 2 and same_lang_met:
            st.success(f"World Language: ✅ {wl_credits}/2 (same language)")
        else:
            st.warning(f"World Language: {wl_credits}/2 (2 years same language required)")
    
        # ---- FINAL STATUS CHECK ----
        all_met = (
            total_credits >= 24 and
            english_credits >= 4 and english_met and
            speech_credits >= 0.5 and
            math_credits >= 3 and
            science_credits >= 3 and
            ss_credits >= 3 and ss_met and
            pe_credits >= 0.5 and health_credits >= 0.5 and
            fine_credits >= 1 and
            wl_credits >= 2 and same_lang_met
        )
    
        if not all_met:
            st.error("Some graduation requirements are still unmet. Please review the categories above.")
        else:
            st.success("✅ All graduation requirements for the University Pathway are complete!")

#----------------------------------------------------------------------------------------------------------------------------------------
#        CAREER AND TECHNICAL GRADUATION PATHWAY TRACKER
#----------------------------------------------------------------------------------------------------------------------------------------
    elif selected_pathway == "Career & Technical":
        st.markdown("### 🛠️ Career & Technical Graduation Tracker")
    
        # Rebuild selected_df
        selected_df_rows = []
        for course_name in st.session_state.ms_credits + sum(st.session_state.course_plan.values(), []):
            if not course_name:
                continue
            row = course_catalog[course_catalog["Course Name"] == course_name]
            if not row.empty:
                selected_df_rows.append(row)
    
        selected_df = pd.concat(selected_df_rows, ignore_index=True) if selected_df_rows else pd.DataFrame(columns=course_catalog.columns)
        selected_df["Course Code"] = selected_df["Course Code"].astype(str)
        selected_df["Credits"] = pd.to_numeric(selected_df["Credits"], errors="coerce")
        selected_df.dropna(subset=["Credits"], inplace=True)
        
        check_for_duplicate_courses(selected_df)
        total_credits = selected_df["Credits"].sum()
        st.markdown(f"**Total Credits:** {total_credits:.1f} / 24 required")
    
        # ---- ENGLISH ----
        required_english_groups = [["2401", "2404"], ["2501", "2504"], ["2601", "2608"], ["2715", "2606"]]
        speech_debate_codes = ["2201", "2205"]
    
        eng_df = selected_df[selected_df["Department"] == "English"]
        valid_english_codes = [code for group in required_english_groups for code in group]
    
        english_grad_df = eng_df[eng_df["Course Code"].isin(valid_english_codes)]
        speech_df = eng_df[eng_df["Course Code"].isin(speech_debate_codes)]
    
        english_credits = english_grad_df["Credits"].sum()
        speech_credits = speech_df["Credits"].sum()
    
        english_met = all(any(code in selected_df["Course Code"].tolist() for code in group) for group in required_english_groups)
    
        if english_credits >= 4 and english_met:
            st.success(f"English: ✅ {english_credits}/4 (group requirements met)")
        else:
            st.warning(f"English: {english_credits}/4 credits — group coverage {'✓' if english_met else '✗'}")
    
        if speech_credits >= 0.5:
            st.success(f"Speech/Debate: ✅ {speech_credits}/0.5")
        else:
            st.warning(f"Speech/Debate: {speech_credits}/0.5")
    
        # ---- MATH CHECK ----
        math_df = selected_df[selected_df["Department"] == "Mathematics"]
        math_credits = math_df["Credits"].sum()
    
        if math_credits >= 3:
            st.success(f"Mathematics: ✅ {math_credits}/3")
        else:
            st.warning(f"Mathematics: {math_credits}/3 (check coverage)")
    
        # ---- SCIENCE ----
        sci_df = selected_df[selected_df["Department"] == "Science"]
        sci_credits = sci_df["Credits"].sum()
        if sci_credits >= 3:
            st.sidebar.success(f"Science: ✅ {sci_credits}/3 credits")
        else:
            st.sidebar.warning(f"Science: {sci_credits}/3 credits")
    
        # ---- SOCIAL STUDIES CHECK ----
        ss_df = selected_df[selected_df["Department"] == "Social Studies"]
        ss_credits = ss_df["Credits"].sum()
        ss_codes = ss_df["Course Code"].tolist()
    
        ss_required = {
            "Geography": ["8101"],
            "World History": ["8201"],
            "U.S. History": ["8304","8310"],
            "U.S. Government": ["8401","8405"]
        }
        ss_met = all(any(code in ss_codes for code in group) for group in ss_required.values())
    
        if ss_credits >= 3 and ss_met:
            st.success(f"Social Studies: ✅ {ss_credits}/3 (required classes met)")
        else:
            st.warning(f"Social Studies: {ss_credits}/3 (check required coverage)")
        claimed_courses.update(ss_df["Course Code"])
    
        # --- Finance (8701) or Personal Finance (9120) ---
        finance_codes = ["8701", "9120"]
        finance_df = selected_df[selected_df["Course Code"].isin(finance_codes)]
        finance_credits = finance_df["Credits"].sum()
        if finance_credits >= 0.5:
            st.success(f"Econ/Finance: ✅ {finance_credits}/0.5")
        else:
            st.warning(f"Econ/Finance: {finance_credits}/0.5")
        claimed_courses.update(finance_df["Course Code"])

        # ---- Native American Studies ----
        na_studies_df = selected_df[selected_df["Course Code"].astype(str) == "8410"]
        na_credits = na_studies_df["Credits"].sum()
        
        if na_credits >= 0.5:
            st.success(f"Native American Studies: ✅ {na_credits}/0.5")
        else:
            st.warning(f"Native American Studies: {na_credits}/0.5")
    
        # --- PE/Health ---
        pe_df = selected_df[
            (selected_df["Department"] == "Physical Education") &
            (selected_df["Course Name"] != "Health Education")
        ]

        pe_credits = pe_df["Credits"].sum()
        health_df = selected_df[selected_df["Course Name"].str.contains("Health", case=False, na=False)]
        health_credits = health_df["Credits"].sum()
    
        if pe_credits >= 0.5 and health_credits >= 0.5:
            st.success(f"PE/Health: ✅ PE {pe_credits}, Health {health_credits} (1.0 total)")
        else:
            st.warning(f"PE/Health: PE {pe_credits}, Health {health_credits} (1.0 total)")
        claimed_courses.update(pe_df["Course Code"])
        claimed_courses.update(health_df["Course Code"])
    
        # ---- FINE ARTS ----
        fine_arts_df = selected_df[selected_df["Department"].isin(["Visual Arts", "Vocal Music", "Performing Arts", "Fine Arts"])]
        fine_credits = fine_arts_df["Credits"].sum()
        if fine_credits >= 1:
            st.sidebar.success(f"Fine Arts: ✅ {fine_credits}/1 credit")
        else:
            st.sidebar.warning(f"Fine Arts: {fine_credits}/1 credit")
    
        # ---- CTE CLUSTER CHECK----
        cte_df = selected_df[selected_df["Department"].isin(["CTE", "Business", "Computer Science"])]
        cte_df["Course Code"] = cte_df["Course Code"].astype(str)
        
        cluster_hits = {}
        for cluster, codes in cte_cluster_map.items():
            matched = cte_df[cte_df["Course Code"].isin(codes)]
            total_cluster_credits = matched["Credits"].sum()
            codes_taken = set(matched["Course Code"])
            all_courses_completed = codes_taken == set(codes)
        
            if all_courses_completed or total_cluster_credits >= 1.5:
                cluster_hits[cluster] = total_cluster_credits
        
        if cluster_hits:
            matched_cluster = max(cluster_hits, key=cluster_hits.get)
            st.sidebar.success(
                f"✅ Completed CTE cluster: **{matched_cluster}** ({cluster_hits[matched_cluster]} credits)"
            )
        else:
            st.sidebar.warning("CTE cluster requirement not met")

        # ---- FINAL STATUS CHECK ----
        all_met = (
            total_credits >= 24 and
            english_credits >= 4 and english_met and
            speech_credits >= 0.5 and
            math_credits >= 3 and
            sci_credits >= 3 and
            ss_credits >= 3 and ss_met and
            pe_credits >= 0.5 and health_credits >= 0.5 and
            fine_credits >= 1
        )
    
        if not all_met:
            st.error("Some graduation requirements are still unmet. Please review the categories above.")
        else:
            st.success("✅ All graduation requirements for the Career & Technical Pathway are complete!")

#------------------------------------------------------------------------------------------------------------------------------------
#               HONORS/ADVANCED ENDORSEMENT PATHWAY
#------------------------------------------------------------------------------------------------------------------------------------

    elif selected_pathway == "Honors/Scholarship Opportunity":
        st.markdown("🏅 **Advanced/Honors Endorsement Tracker**")
    
        claimed_courses = set()    
        selected_df_rows = []
        for course_name in st.session_state.ms_credits + sum(st.session_state.course_plan.values(), []):
            if not course_name:
                continue
            row = course_catalog[course_catalog["Course Name"] == course_name]
            if not row.empty:
                selected_df_rows.append(row)

        selected_df = pd.concat(selected_df_rows, ignore_index=True) if selected_df_rows else pd.DataFrame(columns=course_catalog.columns)        
        selected_df["Course Code"] = selected_df["Course Code"].astype(str)
        selected_df["Credits"] = pd.to_numeric(selected_df["Credits"], errors="coerce")
        selected_df.dropna(subset=["Credits"], inplace=True)
        check_for_duplicate_courses(selected_df)

        total_credits = selected_df["Credits"].sum()
        st.markdown(f"**Total Credits:** {total_credits:.1f} / 24 required")
    
        # ---- LANGUAGE ARTS ----
        required_english_groups = [["2401", "2404"], ["2501", "2504"], ["2601", "2608"], ["2715", "2606"]]
        speech_debate_codes = ["2201", "2205"]
        
        eng_df = selected_df[selected_df["Department"] == "English"]
        valid_english_codes = [code for group in required_english_groups for code in group]
        
        english_grad_df = eng_df[eng_df["Course Code"].astype(str).isin(valid_english_codes)]
        speech_df = eng_df[eng_df["Course Code"].astype(str).isin(speech_debate_codes)]
        extra_english_df = eng_df[
            ~eng_df["Course Code"].astype(str).isin(valid_english_codes + speech_debate_codes)
        ]
        
        english_credits = english_grad_df["Credits"].sum()
        speech_credits = speech_df["Credits"].sum()
        english_met = all(any(code in selected_codes for code in group) for group in required_english_groups)
        
        if english_credits >= 4 and english_met:
            st.success(f"English: ✅ {english_credits}/4 (group requirements met)")
        else:
            st.warning(f"English: {english_credits}/4 credits — group coverage {'✓' if english_met else '✗'}")
        
        if speech_credits >= 0.5:
            st.success(f"Speech/Debate: ✅ {speech_credits}/0.5")
        else:
            st.warning(f"Speech/Debate: {speech_credits}/0.5")

        # --- Math ---
        required_math_groups = [["4301", "4304"], ["4401", "4402"], ["4506", "4504"]]
        advanced_math_codes = ["4502"] + [code for code in selected_df["Course Code"] if code.isdigit() and int(code) > 4600]
        math_df = selected_df[selected_df["Department"] == "Mathematics"]
        math_codes = set(math_df["Course Code"])
        math_credits = math_df["Credits"].sum()
    
        math_met = all(any(code in math_codes for code in group) for group in required_math_groups)
        adv_math_met = any(code in math_codes for code in advanced_math_codes)
    
        if math_met and adv_math_met and math_credits >= 4:
            st.success(f"Mathematics: ✅ {math_credits}/4 (Algebra I, Geometry, Algebra II + Adv Math)")
        else:
            st.warning(f"Mathematics: {math_credits}/4 (check coverage)")
        claimed_courses.update(math_df["Course Code"])
    
        # --- Science ---
        sci_df = selected_df[selected_df["Department"] == "Science"]
        sci_codes = sci_df["Course Code"]
        sci_credits = sci_df["Credits"].sum()
    
        bio_met = "7201" in sci_codes.values
        chem_met = "7301" in sci_codes.values
        physci_met = "7101" in sci_codes.values
        other_sci_credit = sci_credits >= 4
    
        if bio_met and chem_met and physci_met and other_sci_credit:
            st.success(f"Science: ✅ {sci_credits}/4 (Bio, Chem, PhysSci + elective)")
        else:
            st.warning(f"Science: {sci_credits}/4 (check coverage)")
        claimed_courses.update(sci_df["Course Code"])
    
        # --- Social Studies ---
        ss_df = selected_df[selected_df["Department"] == "Social Studies"]
        ss_credits = ss_df["Credits"].sum()
        ss_codes = ss_df["Course Code"].tolist()
    
        ss_required = {
            "Geography": ["8101"],
            "World History": ["8201"],
            "U.S. History": ["8304","8310"],
            "U.S. Government": ["8401","8405"]
        }
        ss_met = all(any(code in ss_codes for code in group) for group in ss_required.values())
    
        if ss_credits >= 3 and ss_met:
            st.success(f"Social Studies: ✅ {ss_credits}/3 (required classes met)")
        else:
            st.warning(f"Social Studies: {ss_credits}/3 (check required coverage)")
        claimed_courses.update(ss_df["Course Code"])
    
        # --- Finance (8701) or Personal Finance (9120) ---
        finance_codes = ["8701", "9120"]
        finance_df = selected_df[selected_df["Course Code"].isin(finance_codes)]
        finance_credits = finance_df["Credits"].sum()
        if finance_credits >= 0.5:
            st.success(f"Econ/Finance: ✅ {finance_credits}/0.5")
        else:
            st.warning(f"Econ/Finance: {finance_credits}/0.5")
        claimed_courses.update(finance_df["Course Code"])

        # ---- Native American Studies ----
        na_studies_df = selected_df[selected_df["Course Code"].astype(str) == "8410"]
        na_credits = na_studies_df["Credits"].sum()
        
        if na_credits >= 1.0:
            st.success(f"Native American Studies: ✅ {na_credits}/0.5")
        else:
            st.warning(f"Native American Studies: {na_credits}/0.5")

        # --- PE/Health ---
        pe_df = selected_df[
            (selected_df["Department"] == "Physical Education") &
            (selected_df["Course Name"] != "Health Education")
        ]

        pe_credits = pe_df["Credits"].sum()
        health_df = selected_df[selected_df["Course Name"].str.contains("Health", case=False, na=False)]
        health_credits = health_df["Credits"].sum()
    
        if pe_credits >= 0.5 and health_credits >= 0.5:
            st.success(f"PE/Health: ✅ PE {pe_credits}, Health {health_credits} (1.0 total)")
        else:
            st.warning(f"PE/Health: PE {pe_credits}, Health {health_credits} (1.0 total)")
        claimed_courses.update(pe_df["Course Code"])
        claimed_courses.update(health_df["Course Code"])
    
        # --- Fine Arts ---
        fine_df = selected_df[
            selected_df["Department"].isin([
                "Fine Arts", "Vocal Music", "Performing Arts", "Visual Arts"
            ])
        ]        
        
        fine_credits = fine_df["Credits"].sum()
        if fine_credits >= 1:
            st.success(f"Fine Arts: ✅ {fine_credits}/1.0")
        else:
            st.warning(f"Fine Arts: {fine_credits}/1.0")
        claimed_courses.update(fine_df["Course Code"])
    
        # --- World Language or CTE Cluster ---
        lang_df = selected_df[selected_df["Department"] == "World Languages"]
        lang_credits = lang_df["Credits"].sum()
    
        # CTE cluster logic
        cte_df = selected_df[selected_df["Department"].isin(["CTE", "Business", "Computer Science"])]
        cte_df["Course Code"] = cte_df["Course Code"].astype(str)
    
        cluster_hits = {}
        for cluster, codes in cte_cluster_map.items():
            matched = cte_df[cte_df["Course Code"].isin(codes)]
            total_cluster_credits = matched["Credits"].sum()
            codes_taken = set(matched["Course Code"])
            all_courses_completed = codes_taken == set(codes)
    
            if all_courses_completed or total_cluster_credits >= 1.5:
                cluster_hits[cluster] = total_cluster_credits
    
        if lang_credits >= 2:
            st.success(f"Languages: ✅ {lang_credits}/2 credits in World Languages")
        elif cluster_hits:
            matched_cluster = max(cluster_hits, key=cluster_hits.get)
            st.success(f"✅ Completed CTE cluster: **{matched_cluster}** ({cluster_hits[matched_cluster]} credits)")
        else:
            st.warning("World Language or CTE cluster requirement not met")
    
        # --- Final Graduation Check ---
        if (
            english_credits >= 4 and
            math_met and adv_math_met and math_credits >= 4 and
            bio_met and chem_met and physci_met and sci_credits >= 4 and
            ss_met and ss_credits >= 3 and
            pe_credits >= 0.5 and health_credits >= 0.5 and
            fine_credits >= 1 and
            (lang_credits >= 2 or cluster_hits) and
            total_credits >= 24
        ):
            st.success("🎓 All Advanced/Honors Endorsement graduation requirements met!")
        else:
            st.warning("Some graduation requirements are still unmet. Please review the categories above.")


# Call tracker in right-hand sidebar
with st.sidebar:
    department_sidebar()
    show_graduation_tracker()
