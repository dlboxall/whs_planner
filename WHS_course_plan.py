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
catalog_path = "WHS_course_catalog_enriched.csv"
@st.cache_data
def load_course_catalog():
    df = pd.read_csv(catalog_path)
    df["Grade Levels"] = df["Grade Levels"].astype(str)  # Ensure string type for filtering
    return df

course_catalog = load_course_catalog()

# --- Section 1: Career Pathways (placeholder) ---
if section == "Career Pathways":
    st.header("🎓 Career Pathways")
    st.info("Select a career interest to explore relevant courses. Coming soon!")

# --- Section 2: Course Planner ---
elif section == "Course Planner":
    st.header("📋 4-Year Course Planning Grid")

    # Define 8 entries per year level
    years = ["9th Grade", "10th Grade", "11th Grade", "12th Grade"]
    row_labels = [f"Course {i+1}" for i in range(8)]

    if "course_plan" not in st.session_state:
        st.session_state.course_plan = {
            year: ["" for _ in range(8)] for year in years
        }

    for year in years:
        st.subheader(year)
        cols = st.columns(4)

        # Get course list for that grade
        grade_filter = year.split()[0]  # e.g., "9"
        grade_courses = course_catalog[course_catalog["Grade Levels"].str.contains(grade_filter, na=False)]
        options = [""] + sorted(grade_courses["Course Name"].unique().tolist())

        for i in range(8):
            col = cols[i % 4]  # Arrange 4 per row
            with col:
                selected_course = st.selectbox(
                    label=f"{year} - {row_labels[i]}",
                    options=options,
                    index=options.index(st.session_state.course_plan[year][i]) if st.session_state.course_plan[year][i] in options else 0,
                    key=f"{year}_{i}"
                )
                st.session_state.course_plan[year][i] = selected_course

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
