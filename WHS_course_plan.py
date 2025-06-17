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
#department_sidebar()

st.markdown("## 📘 WHS Course Planner Dashboard")

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

                # Initialize the session value if not already set
                if course_code_key not in st.session_state:
                    st.session_state[course_code_key] = ""

                # Create the input box (value persists due to key only)
                st.text_input(
                    f"Enter 3-letter code for Course {i+1}",
                    max_chars=3,
                    key=course_code_key
                )

                # Read from session and normalize
                course_code = st.session_state[course_code_key].strip().upper()

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




def show_graduation_tracker():
    st.markdown("### 🎓 Graduation Tracker")

    selected_pathway = st.session_state.get("grad_pathway", "University")

    if selected_pathway == "University":
        # Extract selected course codes and names
        selected_codes = []
        selected_names = []
        for year in st.session_state.course_plan:
            for course_name in st.session_state.course_plan[year]:
                if not course_name:
                    continue
                row = course_catalog[course_catalog["Course Name"] == course_name]
                if row.empty:
                    continue
                selected_codes.append(str(row["Course Code"].values[0]))
                selected_names.append(row["Course Name"].values[0])
    
        graduation_df = course_catalog.copy()
        graduation_df["Credits"] = 1  # Default 1 credit each
        selected_df = graduation_df[graduation_df["Course Name"].isin(selected_names)]
    
        # --- LANGUAGE ARTS ---
        eng_df = selected_df[selected_df["Department"] == "English"]
        eng_credits = eng_df["Credits"].sum()
        required_english_groups = [["2401", "2404"], ["2501", "2504"], ["2601", "2608"], ["2715", "2606"]]
        english_met = all(any(code in selected_codes for code in group) for group in required_english_groups)
    
        if eng_credits >= 4 and english_met:
            st.success(f"English: ✅ {eng_credits}/4 (group requirements met)")
        else:
            st.warning(f"English: {eng_credits}/4 credits — group coverage {'✓' if english_met else '✗'}")
    
        # --- MATHEMATICS ---
        math_df = selected_df[selected_df["Department"] == "Mathematics"]
        math_credits = math_df["Credits"].sum()
        required_math_groups = [["4301", "4304"], ["4401", "4402"], ["4506", "4504"]]
        math_met = all(any(code in selected_codes for code in group) for group in required_math_groups)
    
        if math_credits >= 3 and math_met:
            st.success(f"Mathematics: ✅ {math_credits}/3 (Algebra I, Geometry, Algebra II)")
        else:
            st.warning(f"Mathematics: {math_credits}/3 credits — group coverage {'✓' if math_met else '✗'}")
    
        # TODO: Add Science, Social Studies, etc.
        st.info("✅ Partial University credit checks complete. Add other subjects next.")
    

        dept_count = {key: 0 for key in tracker}
        for year in st.session_state.course_plan:
            for i, course_name in enumerate(st.session_state.course_plan[year]):
                if not course_name:
                    continue
                row = course_catalog[course_catalog["Course Name"] == course_name]
                if row.empty:
                    continue
                dept = row["Department"].values[0]

                if dept == "English":
                    dept_count["English"] += 1
                elif dept == "Mathematics":
                    dept_count["Mathematics"] += 1
                elif dept == "Science":
                    dept_count["Science"] += 1
                elif dept == "Social Studies":
                    dept_count["Social Studies"] += 1
                elif dept in ["Fine Arts", "Vocal Music", "Performing Arts", "Visual Arts"]:
                    dept_count["Fine Arts / Performing Arts"] += 1
                elif dept == "Physical Education":
                    dept_count["Physical Education"] += 1
                else:
                    dept_count["Electives"] += 1

        all_met = True
        for area, required in tracker.items():
            earned = dept_count[area]
            if earned < required:
                st.warning(f"{area}: {earned}/{required} credits")
                all_met = False
            else:
                st.success(f"{area}: ✅ {earned}/{required}")

        if all_met:
            st.success("🎉 All University graduation requirements met!")
        else:
            st.info("📌 Still working toward full University requirements.")

    elif selected_pathway == "Career & Technical":
        st.info("📋 Career & Technical graduation tracker coming soon...")

    elif selected_pathway == "Honors/Scholarship Opportunity":
        st.info("📋 Honors/Scholarship Opportunity tracker coming soon...")

# Call tracker in right-hand sidebar
with st.sidebar:
    department_sidebar()
    show_graduation_tracker()
