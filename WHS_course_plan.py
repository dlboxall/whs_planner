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

# --- Mock course data ---
mock_courses = [
    "English 9", "Biology", "Algebra I", "World Geography",
    "Speech", "Physical Education", "Spanish I", "Introduction to Business"
]

# --- Section 1: Career Pathways (placeholder) ---
if section == "Career Pathways":
    st.header("🎓 Career Pathways")
    st.info("Select a career interest to explore relevant courses. Coming soon!")

# --- Section 2: Course Planner ---
elif section == "Course Planner":
    st.header("📋 4-Year Course Planning Grid")

    # Columns for years and blocks
    years = ["9th Grade", "10th Grade", "11th Grade", "12th Grade"]
    blocks = ["Block 1", "Block 2", "Block 3", "Block 4"]

    # Generate initial empty grid (16 blocks)
    planner_data = pd.DataFrame("", index=years, columns=blocks)

    if "course_plan" not in st.session_state:
        st.session_state.course_plan = planner_data.copy()

    st.markdown("_Click in a cell to enter a course name. You may also add a grade received (e.g., 'Biology - A')._")
    edited_df = st.data_editor(
        st.session_state.course_plan,
        use_container_width=True,
        num_rows="fixed"
    )

    st.session_state.course_plan = edited_df

# --- Section 3: Graduation & Scholarships ---
elif section == "Graduation & Scholarships":
    st.header("🏆 Graduation Requirements Tracker")
    st.warning("This section will evaluate your plan based on WHS graduation requirements and SD scholarships. Coming soon!")

# --- Section 4: Export Plan ---
elif section == "Export Plan":
    st.header("📄 Export Course Plan to PDF")

    def create_pdf_from_plan(plan_df):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="WHS Course Plan", ln=True, align="C")
        pdf.ln(10)

        for year in plan_df.index:
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(200, 10, txt=year, ln=True)
            pdf.set_font("Arial", size=11)
            for block in plan_df.columns:
                course = plan_df.loc[year, block]
                if course.strip():
                    pdf.cell(200, 8, txt=f"  {block}: {course}", ln=True)
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

