#!/usr/bin/env python
# coding: utf-8

# ## WHS Course Planner App

# In[ ]:

import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="WHS Course Planner", layout="wide")
st.title("📘 WHS Course Planner Dashboard")

st.sidebar.header("Navigation")
section = st.sidebar.radio("Go to:", ["Career Pathways", "Course Planner", "Graduation & Scholarships", "Export Plan"])

# --- Load full course catalog ---
catalog_path = "WHS_course_catalog_with_prereqs.csv"
@st.cache_data
def load_course_catalog():
    df = pd.read_csv(catalog_path)
    df["Grade Levels"] = df["Grade Levels"].astype(str)
    df["Tags"] = df["Tags"].fillna("")
    df["Prerequisites"] = df["Prerequisites"].fillna("")
    return df

course_catalog = load_course_catalog()

# --- Helper functions ---
def is_grade_allowed(levels, grade):
    try:
        grade_num = int(grade)
        levels = levels.strip().lower().replace("th", "")
        if '-' in levels:
            start, end = map(int, levels.split('-'))
            return start <= grade_num <= end
        else:
            return int(levels) == grade_num
    except:
        return False

def has_prereq_met(course_name, current_year, course_plan, prereq_dict):
    prereqs = [p.strip() for p in prereq_dict.get(course_name, "").split(",") if p.strip()]
    if not prereqs:
        return True
    prior_courses = []
    for yr in years:
        if years.index(yr) >= years.index(current_year):
            break
        prior_courses += course_plan[yr]
    return all(p in prior_courses for p in prereqs)

# --- Section 1: Career Pathways (placeholder) ---
if section == "Career Pathways":
    st.header("🎓 Career Pathways")
    st.info("Select a career interest to explore relevant courses. Coming soon!")

# --- Section 2: Course Planner ---
elif section == "Course Planner":
    st.header("📋 4-Year Course Planning Grid")

    years = ["9th Grade", "10th Grade", "11th Grade", "12th Grade"]
    row_labels = [f"Course {i+1}" for i in range(8)]

    if "course_plan" not in st.session_state:
        st.session_state.course_plan = {
            year: ["" for _ in range(8)] for year in years
        }

    prereq_dict = dict(zip(course_catalog["Course Name"], course_catalog["Prerequisites"]))

    for year in years:
        st.subheader(year)
        cols = st.columns(4)

        grade_num = year.split()[0].replace("th", "")
        base_courses = course_catalog[course_catalog["Grade Levels"].str.contains(grade_num, na=False)]

        if year != "12th Grade":
            eligible_courses = base_courses[base_courses["Course Name"].apply(
                lambda name: has_prereq_met(name, year, st.session_state.course_plan, prereq_dict)
            )]
        else:
            eligible_courses = base_courses.copy()

        if not eligible_courses.empty:
            excluded_courses = base_courses[~base_courses["Course Name"].isin(eligible_courses["Course Name"])] if year != "12th Grade" else pd.DataFrame()
        else:
            excluded_courses = base_courses.copy() if year != "12th Grade" else pd.DataFrame()

        if not eligible_courses.empty:
            def format_course_name(row):
                name = row["Course Name"]
                tags = row["Tags"]
                if tags:
                    tag_display = " ".join([f"[{tag.strip()}]" for tag in tags.split(",")])
                    return f"{name} {tag_display}"
                return name

            display_options = eligible_courses.apply(format_course_name, axis=1).tolist()
            name_map = dict(zip(display_options, eligible_courses["Course Name"]))
            options = [""] + sorted(display_options)

            for i in range(8):
                col = cols[i % 4]
                with col:
                    selected_display = st.selectbox(
                        label=f"{year} - {row_labels[i]}",
                        options=options,
                        index=options.index(next((k for k, v in name_map.items() if v == st.session_state.course_plan[year][i]), "")) if st.session_state.course_plan[year][i] else 0,
                        key=f"{year}_{i}"
                    )
                    st.session_state.course_plan[year][i] = name_map.get(selected_display, "")
        else:
            st.warning("⚠️ No eligible courses available for this grade level (missing prerequisites?).")

        if not excluded_courses.empty:
            st.markdown("**❌ Courses not shown due to missing prerequisites:**")
            for _, row in excluded_courses.iterrows():
                prereqs = prereq_dict.get(row["Course Name"], "")
                st.markdown(f"- {row['Course Name']}: _requires_ {prereqs}")

        # Requirements checklist display
        st.markdown("**✅ Requirements Check**")
        required = {
            "9th Grade": ["English 9", "Biology"],
            "10th Grade": ["English 10", "Physical Science"],
            "11th Grade": ["English 11", "US History"],
            "12th Grade": ["English 12", "US Government"]
        }
        courses_taken = st.session_state.course_plan[year]
        for req in required.get(year, []):
            if req in courses_taken:
                st.success(f"✓ {req} completed")
            else:
                st.error(f"✗ {req} missing")
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
