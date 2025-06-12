import streamlit as st
import pandas as pd
import ast

from layout import department_sidebar

st.set_page_config(page_title="Graduation Pathways", layout="wide")
st.title("🎓 Graduation Pathways Checker")

# Sidebar codes
department_sidebar()

#st.markdown("## 🎓 Graduation Pathway Tracker")

# Reuse the student name if entered
#student_name = st.session_state.get("student_name", "")
#if student_name:
    #st.markdown(f"### Reviewing graduation progress for **{student_name}**")
#else:
    #st.markdown("### No student name entered yet.")

#st.set_page_config(page_title="Graduation Pathways", layout="wide")
#st.title("🎓 Graduation Pathways Checker")

# Load the course catalog
def load_course_catalog():
    df = pd.read_csv("WHS_course_catalog.csv")
    df["Grade Levels"] = df["Grade Levels"].apply(lambda x: ast.literal_eval(str(x)))
    df["Prerequisites"] = df["Prerequisites"].fillna("None")
    df["Tags"] = df["Tags"].fillna("")
    df["Notes"] = df["Notes"].fillna("")
    df["Course Code"] = df["Course Code"].astype(str)
    return df

course_catalog = load_course_catalog()

# Access saved student course plan
course_plan = st.session_state.get("course_plan", {})
ms_credits = st.session_state.get("ms_credits", [])

# Combine all course names selected
all_courses = [name for year in course_plan for name in course_plan[year] if name]
all_courses += [name for name in ms_credits if name]

# Get the subset of catalog that matches selected courses
selected_df = course_catalog[course_catalog["Course Name"].isin(all_courses)]
selected_codes = set(selected_df["Course Code"].tolist())

# Filter to courses that count toward graduation (8th–12th grade)
graduation_df = selected_df[selected_df["Grade Levels"].apply(lambda grades: any(g >= 8 for g in grades))]

# Graduation Pathway Selector
pathway = st.radio("Select Graduation Pathway:", [
    "University",
    "Career & Technical",
    "Honors / Scholarship Opportunity"
])

# Helper for displaying requirements with progress
def display_requirement(requirement_text, earned, required, condition=True):
    if condition and earned >= required:
        st.markdown(f"<div style='color:green'><strong>✅ {requirement_text}: {earned} / {required}</strong></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:red'><strong>❌ {requirement_text}: {earned} / {required}</strong></div>", unsafe_allow_html=True)

# --- UNIVERSITY PATHWAY LOGIC --- #
if pathway == "University":
    st.header("University Pathway Requirements")

    used_codes = set()

    # LANGUAGE ARTS (Only specific English courses count)
    required_english_groups = [["2401", "2404"], ["2501", "2504"], ["2601", "2608"], ["2715", "2606"]]
    eng_df = graduation_df[graduation_df["Department"] == "English"]
    eng_credits = 0.0
    english_met = True
    for group in required_english_groups:
        matched = next((code for code in group if code in selected_codes), None)
        if matched:
            course_row = eng_df[eng_df["Course Code"] == matched]
            if not course_row.empty:
                eng_credits += course_row["Credits"].values[0]
                used_codes.add(matched)
        else:
            english_met = False
    display_requirement("4 Units of Language Arts", eng_credits, 4, condition=english_met)

    # MATHEMATICS (Only Algebra I, Geometry, Algebra II count toward math requirement)
    required_math_groups = [["4301", "4304"], ["4401", "4402"], ["4506", "4504"]]
    math_df = graduation_df[graduation_df["Department"] == "Mathematics"]
    math_credits = 0.0
    math_met = True
    for group in required_math_groups:
        matched = next((code for code in group if code in selected_codes), None)
        if matched:
            course_row = math_df[math_df["Course Code"] == matched]
            if not course_row.empty:
                math_credits += course_row["Credits"].values[0]
                used_codes.add(matched)
        else:
            math_met = False
    display_requirement("3 Units of Math including Algebra I, Geometry, Algebra II", math_credits, 3, condition=math_met)

    # SCIENCE
    sci_df = graduation_df[graduation_df["Department"] == "Science"]
    sci_credits = sci_df["Credits"].sum()
    has_bio = any("Biology" in name for name in selected_df[selected_df["Department"] == "Science"]["Course Name"])
    display_requirement("3 Units of Science including Biology", sci_credits, 3, condition=has_bio)

    # SOCIAL STUDIES
    ss_df = graduation_df[graduation_df["Department"] == "Social Studies"]
    ss_credits = ss_df["Credits"].sum()
    has_us_hist = any("U.S. History" in name for name in selected_df[selected_df["Department"] == "Social Studies"]["Course Name"])
    has_govt = any("Government" in name for name in selected_df[selected_df["Department"] == "Social Studies"]["Course Name"])
    condition = has_us_hist and has_govt
    display_requirement("3 Units of Social Studies (incl. U.S. History & Govt.)", ss_credits, 3, condition)

    # FINE ARTS
    fa_df = graduation_df[graduation_df["Department"] == "Fine Arts"]
    fa_credits = fa_df["Credits"].sum()
    display_requirement("1 Unit of Fine Arts", fa_credits, 1)

    # PHYSICAL EDUCATION
    pe_df = graduation_df[graduation_df["Department"] == "Physical Education"]
    pe_credits = pe_df["Credits"].sum()
    display_requirement("0.5 Unit of Physical Education", pe_credits, 0.5)

    # HEALTH
    health_df = graduation_df[graduation_df["Department"].str.contains("Health")]
    health_credits = health_df["Credits"].sum()
    display_requirement("0.5 Unit of Health or Health Integration", health_credits, 0.5)

    # PERSONAL FINANCE OR ECONOMICS
    pf_df = graduation_df[graduation_df["Course Name"].str.contains("Finance|Economics", case=False)]
    pf_credits = pf_df["Credits"].sum()
    display_requirement("0.5 Unit of Personal Finance or Economics", pf_credits, 0.5)

    # COMBINATION UNIT
    combo_df = graduation_df[graduation_df["Department"].isin([
        "CTE", "World Languages"])]
    combo_credits = combo_df["Credits"].sum()
    display_requirement("1 Unit of Capstone/CTE/World Language", combo_credits, 1)

    # ELECTIVES: all other courses not used elsewhere
    unused_df = graduation_df[~graduation_df["Course Code"].isin(used_codes)]
    elective_credits = unused_df["Credits"].sum()
    display_requirement("5.5 Units of Electives", elective_credits, 22)
