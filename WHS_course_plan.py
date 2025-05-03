import streamlit as st
import pandas as pd
import ast
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="WHS Course Planner", layout="wide")
st.title("📘 WHS Course Planner Dashboard")

st.sidebar.header("Navigation")
section = st.sidebar.radio("Go to:", ["Career Pathways", "Course Planner", "Graduation & Scholarships", "Export Plan"])

catalog_path = "WHS_course_catalog.csv"

@st.cache_data
def load_course_catalog():
    df = pd.read_csv(catalog_path)
    df["Grade Levels"] = df["Grade Levels"].apply(lambda x: ast.literal_eval(str(x)))
    df["Tags"] = df["Tags"].fillna("")
    df["Prerequisites"] = df["Prerequisites"].fillna("None")
    df["Notes"] = df["Notes"].fillna("")

    def normalize_department(dept):
        if isinstance(dept, str):
            dept = dept.strip().lower()
            if dept in ["vocal music", "performing arts"]:
                return "Fine Arts"
            return dept.title()
        return dept

    df["Department"] = df["Department"].apply(normalize_department)
    return df

course_catalog = load_course_catalog()

# Ensure middle school plan is initialized
if "ms_credits" not in st.session_state:
    st.session_state.ms_credits = ["" for _ in range(4)]

# Ensure high school plan is initialized
if "course_plan" not in st.session_state:
    st.session_state.course_plan = {year: ["" for _ in range(8)] for year in ["9th Grade", "10th Grade", "11th Grade", "12th Grade"]}
    st.session_state.course_plan_codes = {year: ["" for _ in range(8)] for year in ["9th Grade", "10th Grade", "11th Grade", "12th Grade"]}

years = ["9th Grade", "10th Grade", "11th Grade", "12th Grade"]
row_labels_fall = ["English", "Mathematics", "Science", "Social Studies"]
row_labels_spring = ["Course 5", "Course 6", "Course 7", "Course 8"]
prereq_dict = dict(zip(course_catalog["Course Code"].astype(str), course_catalog["Prerequisites"]))

# Helper function...
# (rest of the app logic continues here)

# --- Helper: Check Prerequisites ---
def has_prereq_met(course_code, current_year, course_plan_codes, prereq_dict):
    taken = []
    ms_taken = []

    if "ms_credits" in st.session_state:
        ms_credit_names = st.session_state.ms_credits
        for name in ms_credit_names:
            if name.strip() != "":
                match = course_catalog.loc[course_catalog["Course Name"] == name, "Course Code"]
                if not match.empty:
                    ms_taken.append(str(match.values[0]))

    for yr in years:
        if years.index(yr) >= years.index(current_year):
            break
        taken += st.session_state.course_plan_codes[yr]

    raw = prereq_dict.get(course_code, "None")
    if raw == "None":
        return True, False

    try:
        parsed = ast.literal_eval(raw)
        needed = []

        if isinstance(parsed, int) or isinstance(parsed, str):
            needed = [str(parsed)]
        elif isinstance(parsed, list) and all(isinstance(x, list) for x in parsed):
            needed = [str(code) for group in parsed for code in group]
        elif isinstance(parsed, list):
            needed = [str(code) for code in parsed]

        if any(code in taken + ms_taken for code in needed):
            only_ms = all(code not in taken for code in needed) and any(code in ms_taken for code in needed)
            return True, only_ms
        else:
            return False, False
    except:
        return False, False

# --- Section 1: Career Pathways ---
if section == "Career Pathways":
    st.header("\U0001F393 Career Pathways")
    st.info("Select a career interest to explore relevant courses. Coming soon!")

# --- Section 2: Course Planner ---
elif section == "Course Planner":
    st.header("\U0001F4CB 4-Year Course Planning Grid")

    # Middle School Credits Section
    st.subheader("\U0001F4D8 High School Credit Earned in Middle School")
    ms_courses = course_catalog[course_catalog["Grade Levels"].apply(lambda x: 8 in x)]
    ms_options = [""] + ms_courses["Course Name"].tolist()

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

    for year in years:
        st.subheader(year)
        cols = st.columns(4)

        grade_num = int(year.split()[0].replace("th", ""))
        base_courses = course_catalog[course_catalog["Grade Levels"].apply(lambda lst: grade_num in lst)]

        for i in range(8):
            department = row_labels_fall[i] if i < 4 else row_labels_spring[i - 4]
            col = cols[i % 4]
            with col:
                label = f"{year} - {department}"

                dept_courses = base_courses[base_courses["Tags"].str.contains(department, case=False, na=False)]

                if dept_courses.empty:
                    eligible_courses = pd.DataFrame(columns=base_courses.columns)
                    st.info(f"No courses found for department tag '{department}' in {year}.")
                else:
                    if year != "12th Grade":
                        eligible_courses = dept_courses[dept_courses["Course Code"].astype(str).apply(
                            lambda code: has_prereq_met(code, year, st.session_state.course_plan_codes, prereq_dict)[0]
                        )]
                    else:
                        eligible_courses = dept_courses.copy()

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
                        st.caption(f"\u2139\ufe0f {note}")

                    selected_code = code_lookup.get(selected_course, "")
                    _, unlocked_by_ms = has_prereq_met(selected_code, year, st.session_state.course_plan_codes, prereq_dict)
                    if unlocked_by_ms:
                        st.caption("\U0001F393 Eligible because of Middle School Credit! \U0001F389")

# --- Section 3: Graduation & Scholarships ---
elif section == "Graduation & Scholarships":
    st.header("\U0001F3C6 Graduation Requirements Tracker")
    st.warning("Coming soon!")

# --- Section 4: Export Plan ---
elif section == "Export Plan":
    st.header("\U0001F4C4 Export Course Plan to PDF")

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
                    pdf.cell(200, 8, txt=f"  {course}", ln=True)
            pdf.ln(5)

        return pdf.output(dest='S').encode('latin1')

    if st.session_state.course_plan is not None:
        pdf_bytes = create_pdf_from_plan(st.session_state.course_plan)
        st.download_button(
            label="\U0001F4E5 Download PDF",
            data=pdf_bytes,
            file_name="WHS_Course_Plan.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Fill out the course plan before exporting.")
