#!/usr/bin/env python
# coding: utf-8

# ## WHS Course Planner App

# In[ ]:

import streamlit as st
import pandas as pd
import ast
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="WHS Course Planner", layout="wide")
st.title("📘 WHS Course Planner Dashboard")

st.sidebar.header("Navigation")
section = st.sidebar.radio("Go to:", ["Career Pathways", "Course Planner", "Graduation & Scholarships", "Export Plan"])

# --- Load updated course catalog ---
catalog_path = "WHS_course_catalog.csv"
@st.cache_data
def load_course_catalog():
    df = pd.read_csv(catalog_path)
    df["Grade Levels"] = df["Grade Levels"].apply(lambda x: ast.literal_eval(str(x)))
    df["Tags"] = df["Tags"].fillna("")
    df["Prerequisites"] = df["Prerequisites"].fillna("None")
    df["Notes"] = df["Notes"].fillna("")
    return df

course_catalog = load_course_catalog()

# --- Helper functions ---
def has_prereq_met(course_code, current_year, course_plan_codes, prereq_dict):
    taken = []
    for yr in years:
        if years.index(yr) >= years.index(current_year):
            break
        taken += course_plan_codes[yr]

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

# --- Section 1: Career Pathways (placeholder) ---
if section == "Career Pathways":
    st.header("🎓 Career Pathways")
    st.info("Select a career interest to explore relevant courses. Coming soon!")

# --- Section 2: Course Planner ---
elif section == "Course Planner":
    st.header("📋 4-Year Course Planning Grid")

    # --- Middle School Advanced Credit Section ---
    st.subheader("📘 High School Credit Earned in Middle School")
    ms_options = ["", "Integrated Health", "Algebra I", "Geometry", "Algebra II", "Geography", "Band", "Orchestra"]
    if "ms_credits" not in st.session_state:
        st.session_state.ms_credits = ["" for _ in range(4)]

    ms_cols = st.columns(4)
    for i in range(4):
        with ms_cols[i % 4]:
            st.session_state.ms_credits[i] = st.selectbox(
                f"Middle School Course {i+1}",
                ms_options,
                index=ms_options.index(st.session_state.ms_credits[i]) if st.session_state.ms_credits[i] in ms_options else 0,
                key=f"ms_course_{i}"
            )

    st.markdown("---")
    st.header("📋 4-Year Course Planning Grid")

    years = ["9th Grade", "10th Grade", "11th Grade", "12th Grade"]
row_labels_fall = ["English", "Mathematics", "Science", "Social Studies"]
row_labels_spring = ["Course 5", "Course 6", "Course 7", "Course 8"]

if "course_plan" not in st.session_state:
    st.session_state.course_plan = {year: ["" for _ in range(8)] for year in years}
    st.session_state.course_plan_codes = {year: ["" for _ in range(8)] for year in years}

prereq_dict = dict(zip(course_catalog["Course Code"].astype(str), course_catalog["Prerequisites"]))

    for year in years:
    st.subheader(year)

    grade_num = int(year.split()[0].replace("th", ""))
    base_courses = course_catalog[course_catalog["Grade Levels"].apply(lambda lst: grade_num in lst)]

    prereq_taken = []

    # --- Top 4 courses (fall semester)
    fall_cols = st.columns(4)
    for i, label in enumerate(row_labels_fall):
        col = fall_cols[i]
        with col:
            dept_courses = base_courses[base_courses["Department"].str.contains(label, case=False, na=False)]
            eligible_courses = dept_courses[dept_courses["Course Code"].astype(str).apply(
                lambda code: has_prereq_met(code, year, st.session_state.course_plan_codes, prereq_dict)
            )]

            options = [""] + eligible_courses["Course Name"].tolist()
            code_lookup = dict(zip(eligible_courses["Course Name"], eligible_courses["Course Code"].astype(str)))
            notes_lookup = dict(zip(eligible_courses["Course Name"], eligible_courses["Notes"]))

            selected_course = st.selectbox(
                label=f"{year} - {label}",
                options=options,
                index=options.index(st.session_state.course_plan[year][i]) if st.session_state.course_plan[year][i] in options else 0,
                key=f"{year}_{i}"
            )
            st.session_state.course_plan[year][i] = selected_course
            st.session_state.course_plan_codes[year][i] = code_lookup.get(selected_course, "")

            if selected_course:
                prereq_taken.append(code_lookup.get(selected_course, ""))
                note = notes_lookup.get(selected_course, "")
                if note:
                    st.caption(f"ℹ️ {note}")

    # --- Bottom 4 courses (spring semester)
    spring_cols = st.columns(4)
    for j, label in enumerate(row_labels_spring):
        col = spring_cols[j]
        with col:
            eligible_courses = base_courses[base_courses["Course Code"].astype(str).apply(
                lambda code: has_prereq_met(code, year, st.session_state.course_plan_codes, prereq_dict)
            )]

            options = [""] + eligible_courses["Course Name"].tolist()
            code_lookup = dict(zip(eligible_courses["Course Name"], eligible_courses["Course Code"].astype(str)))
            notes_lookup = dict(zip(eligible_courses["Course Name"], eligible_courses["Notes"]))

            selected_course = st.selectbox(
                label=f"{year} - {label}",
                options=options,
                index=options.index(st.session_state.course_plan[year][j+4]) if st.session_state.course_plan[year][j+4] in options else 0,
                key=f"{year}_{j+4}"
            )
            st.session_state.course_plan[year][j+4] = selected_course
            st.session_state.course_plan_codes[year][j+4] = code_lookup.get(selected_course, "")

            if selected_course:
                note = notes_lookup.get(selected_course, "")
                if note:
                    st.caption(f"ℹ️ {note}")

    st.markdown("---")

# --- Section 3: Graduation & Scholarships ---
elif section == "Graduation & Scholarships":
    st.header("🏆 Graduation Requirements Tracker")
    st.warning("This section will evaluate your plan based on WHS graduation requirements and SD scholarships. Coming soon!")

# --- Section 4: Export Plan ---
elif section == "Export Plan":
    st.header("📄 Export Course Plan to PDF")

    def create_pdf_from_plan(course_dict):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="WHS Course Plan", ln=True, align="C")
        pdf.ln(10)

        for year, course_list in course_dict.items():
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(200, 10, txt=year, ln=True)
            pdf.set_font("Arial", size=11)
            for i, course in enumerate(course_list):
                if course.strip():
                    pdf.cell(200, 8, txt=f"  Course {i+1}: {course}", ln=True)
            pdf.ln(5)

        return pdf.output(dest='S').encode('latin1')

    if st.session_state.course_plan is not None:
        pdf_bytes = create_pdf_from_plan(st.session_state.course_plan)
        st.download_button(
            label="📥 Download PDF",
            data=pdf_bytes,
            file_name="WHS_Course_Plan.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Fill out the course plan before exporting.")
