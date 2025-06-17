import streamlit as st
import pandas as pd
import ast
from layout import department_sidebar

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

st.set_page_config(page_title="WHS Course Planner", layout="wide")

# Show sidebar codes
department_sidebar()

st.markdown("## 📘 WHS Course Planner Dashboard")

# Student input
st.markdown("### Course plan created for:")
student_name = st.text_input("Enter student name", key="student_name")

#st.markdown("## High School Credit Earned in Middle School")

#st.set_page_config(page_title="WHS Course Planner", layout="wide")
#st.title("📘 WHS Course Planner Dashboard")
#st.markdown("### Course plan created for:")
#student_name = st.text_input("Enter student name", key="student_name")

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

# Main planner loop
for year in years:
    st.header(year)
    cols = st.columns(4)
    grade_num = int(year.split()[0].replace("th", "").replace("st", "").replace("nd", "").replace("rd", ""))
    base_courses = course_catalog[course_catalog["Grade Levels"].apply(lambda x: grade_num in x)]

    for i in range(8):
        department = row_labels_fall[i] if i < 4 else row_labels_spring[i - 4]
        col = cols[i % 4]
        with col:
            label = f"{year} – {department}"

            if i < 4:
                # --- Core subjects: dropdown selection by department ---
                dept_courses = base_courses[base_courses["Department"] == department]
                eligible_courses = dept_courses[dept_courses["Course Code"].astype(str).apply(
                    lambda code: has_prereq_met(code, year, st.session_state.course_plan_codes, prereq_dict, i)
                )]

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
                # --- Electives: text input for 3-letter department code ---
                course_code_key = f"{year}_{i}_code"

                # Ensure the session value is initialized
                if course_code_key not in st.session_state:
                    st.session_state[course_code_key] = ""
                
                # Text input reads the current session value, and reuses its key
                course_code_input = st.text_input(
                    f"Enter 3-letter code for Course {i+1}",
                    value=st.session_state[course_code_key],
                    max_chars=3,
                    key=course_code_key).strip()
                
                # Always update the session state explicitly from the user's input
                #st.session_state[course_code_key] = course_code_input
                course_code = course_code_input.upper()

                # Get mapped department name(s)
                department_names = dept_code_to_name.get(course_code, [])

                if isinstance(department_names, str):
                    department_names = [department_names]  # Normalize to list

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

            
if False:
    # this code will never run
    st.write("Temporarily disabled")

    # old main loop
    if i < 4:
        dept_courses = base_courses[base_courses["Department"] == department]
        eligible_courses = dept_courses[dept_courses["Course Code"].astype(str).apply(
            lambda code: has_prereq_met(code, year, st.session_state.course_plan_codes, prereq_dict, i)
        )]
    else:
        all_departments = sorted(base_courses["Department"].dropna().unique())
        selected_dept = st.selectbox(f"Select Department ({department})", [""] + all_departments, key=f"{year}_dept_{i}")
        if selected_dept:
            dept_courses = base_courses[base_courses["Department"] == selected_dept]
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
    st.markdown("---")

