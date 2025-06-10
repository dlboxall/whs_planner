import streamlit as st
import pandas as pd
import ast
import datetime

st.set_page_config(page_title="WHS Course Planner", layout="wide")
st.title("📘 WHS Course Planner Dashboard")

# Load course catalog
def load_course_catalog():
    df = pd.read_csv("WHS_course_catalog.csv")
    df["Grade Levels"] = df["Grade Levels"].apply(lambda x: ast.literal_eval(str(x)))
    df["Prerequisites"] = df["Prerequisites"].fillna("None")
    df["Tags"] = df["Tags"].fillna("")
    df["Notes"] = df["Notes"].fillna("")
    return df

course_catalog = load_course_catalog()

# Grade level structure
years = ["9th Grade", "10th Grade", "11th Grade", "12th Grade"]
row_labels_fall = ["English", "Mathematics", "Science", "Social Studies"]
row_labels_spring = ["Course 5", "Course 6", "Course 7", "Course 8"]

#Add in extra loop below
import datetime

# Student name input and export button
student_name = st.text_input("Student Name", key="student_name_input")
if st.button("📄 Export Schedule to PDF", key="export_schedule_button"):
    from io import BytesIO
    import pdfkit
    import pandas as pd
    from jinja2 import Template

    # Build course plan table
    course_data = []
    for year in years:
        sem1 = [c for i, c in enumerate(st.session_state.course_plan[year]) if i < 4 and c]
        sem2 = [c for i, c in enumerate(st.session_state.course_plan[year]) if i >= 4 and c]
        course_data.append({
            "year": year,
            "sem1": ", ".join(sem1),
            "sem2": ", ".join(sem2)
        })

    # Graduation summary logic (basic stub for placeholder)
    grad_summary = [
        {"label": "4 Units of Language Arts", "value": "TBD", "met": False},
        {"label": "3 Units of Mathematics", "value": "TBD", "met": False},
        {"label": "3 Units of Science", "value": "TBD", "met": False},
        {"label": "3 Units of Social Studies", "value": "TBD", "met": False},
        {"label": "1 Unit of Fine Arts", "value": "TBD", "met": False},
        {"label": "0.5 Unit of PE", "value": "TBD", "met": False},
        {"label": "0.5 Unit of Health", "value": "TBD", "met": False},
        {"label": "0.5 Unit of Personal Finance", "value": "TBD", "met": False},
        {"label": "1 Unit of Capstone/CTE/World Language", "value": "TBD", "met": False},
        {"label": "5.5 Units of Electives", "value": "TBD", "met": False}
    ]

    # Generate HTML using Jinja2 template
    timestamp = datetime.datetime.now().strftime("%B %d, %Y – %I:%M %p")
    template_str = """
    <html>
    <head><style>
        body { font-family: Arial; margin: 40px; }
        h1 { font-size: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #999; padding: 8px; text-align: left; }
        .check { color: green; font-weight: bold; }
        .cross { color: red; font-weight: bold; }
    </style></head>
    <body>
        <h1>Course Plan for {{ student_name }}</h1>
        <p><em>Printed: {{ timestamp }}</em></p>

        <table>
            <tr><th>Year</th><th>Semester 1 Courses</th><th>Semester 2 Courses</th></tr>
            {% for row in data %}
            <tr><td>{{ row.year }}</td><td>{{ row.sem1 }}</td><td>{{ row.sem2 }}</td></tr>
            {% endfor %}
        </table>

        <h2 style='margin-top:40px;'>Graduation Pathway Summary</h2>
        <table>
            <tr><th>Status</th><th>Requirement</th><th>Progress</th></tr>
            {% for item in grad %}
            <tr>
                <td class="{{ 'check' if item.met else 'cross' }}">{{ '✅' if item.met else '❌' }}</td>
                <td>{{ item.label }}</td>
                <td>{{ item.value }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """

    from jinja2 import Template
    template = Template(template_str)
    html_content = template.render(
        student_name=student_name or "(Unnamed Student)",
        data=course_data,
        grad=grad_summary,
        timestamp=timestamp
    )

    # Convert to PDF
    pdf_bytes = pdfkit.from_string(html_content, False)
    st.download_button("📥 Download PDF", pdf_bytes, file_name="WHS_Course_Schedule.pdf", mime="application/pdf")

# Ensure ms_credits is initialized
if "ms_credits" not in st.session_state:
    st.session_state.ms_credits = ["" for _ in range(4)]

# Middle School Credits
st.header("High School Credit Earned in Middle School")
ms_courses = course_catalog[course_catalog["Grade Levels"].apply(lambda x: 8 in x)]
ms_options = ["" ] + ms_courses["Course Name"].tolist()
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

    # Build course plan table
    course_data = []
    for year in years:
        sem1 = [c for i, c in enumerate(st.session_state.course_plan[year]) if i < 4 and c]
        sem2 = [c for i, c in enumerate(st.session_state.course_plan[year]) if i >= 4 and c]
        course_data.append({
            "year": year,
            "sem1": ", ".join(sem1),
            "sem2": ", ".join(sem2)
        })

    # Graduation summary logic (basic stub for placeholder)
    grad_summary = [
        {"label": "4 Units of Language Arts", "value": "TBD", "met": False},
        {"label": "3 Units of Mathematics", "value": "TBD", "met": False},
        {"label": "3 Units of Science", "value": "TBD", "met": False},
        {"label": "3 Units of Social Studies", "value": "TBD", "met": False},
        {"label": "1 Unit of Fine Arts", "value": "TBD", "met": False},
        {"label": "0.5 Unit of PE", "value": "TBD", "met": False},
        {"label": "0.5 Unit of Health", "value": "TBD", "met": False},
        {"label": "0.5 Unit of Personal Finance", "value": "TBD", "met": False},
        {"label": "1 Unit of Capstone/CTE/World Language", "value": "TBD", "met": False},
        {"label": "5.5 Units of Electives", "value": "TBD", "met": False}
    ]

    # Generate HTML using Jinja2 template
    timestamp = datetime.datetime.now().strftime("%B %d, %Y – %I:%M %p")
    template_str = """
    <html>
    <head><style>
        body { font-family: Arial; margin: 40px; }
        h1 { font-size: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #999; padding: 8px; text-align: left; }
        .check { color: green; font-weight: bold; }
        .cross { color: red; font-weight: bold; }
    </style></head>
    <body>
        <h1>Course Plan for {{ student_name }}</h1>
        <p><em>Printed: {{ timestamp }}</em></p>

        <table>
            <tr><th>Year</th><th>Semester 1 Courses</th><th>Semester 2 Courses</th></tr>
            {% for row in data %}
            <tr><td>{{ row.year }}</td><td>{{ row.sem1 }}</td><td>{{ row.sem2 }}</td></tr>
            {% endfor %}
        </table>

        <h2 style='margin-top:40px;'>Graduation Pathway Summary</h2>
        <table>
            <tr><th>Status</th><th>Requirement</th><th>Progress</th></tr>
            {% for item in grad %}
            <tr>
                <td class="{{ 'check' if item.met else 'cross' }}">{{ '✅' if item.met else '❌' }}</td>
                <td>{{ item.label }}</td>
                <td>{{ item.value }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """

    from jinja2 import Template
    template = Template(template_str)
    html_content = template.render(
        student_name=student_name or "(Unnamed Student)",
        data=course_data,
        grad=grad_summary,
        timestamp=timestamp
    )

    # Convert to PDF
    pdf_bytes = pdfkit.from_string(html_content, False)
    st.download_button("📥 Download PDF", pdf_bytes, file_name="WHS_Course_Schedule.pdf", mime="application/pdf")




# Initialize session state
if "course_plan" not in st.session_state:
    st.session_state.course_plan = {year: ["" for _ in range(8)] for year in years}
    st.session_state.course_plan_codes = {year: ["" for _ in range(8)] for year in years}
if "ms_credits" not in st.session_state:
    st.session_state.ms_credits = ["" for _ in range(4)]

# Build prerequisite dictionary
prereq_dict = dict(zip(course_catalog["Course Code"].astype(str), course_catalog["Prerequisites"]))

# Helper to check if prerequisites are met
def has_prereq_met(course_code, current_year, course_plan_codes, prereq_dict, current_index):
    taken = []
    for name in st.session_state.ms_credits:
        if name:
            code = course_catalog.loc[course_catalog["Course Name"] == name, "Course Code"]
            if not code.empty:
                taken.append(str(code.values[0]))

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
        if isinstance(parsed, (int, str)):
            return str(parsed) in taken
        elif isinstance(parsed, list) and all(isinstance(x, list) for x in parsed):
            return all(any(str(code) in taken for code in group) for group in parsed)
        elif isinstance(parsed, list):
            return any(str(code) in taken for code in parsed)
        else:
            return False
    except:
        return False

# Student name input and export button
student_name = st.text_input("Student Name")
if st.button("📄 Export Schedule to PDF"):
    from io import BytesIO
    import pdfkit
    from jinja2 import Template

    # Build course plan table
    course_data = []
    for year in years:
        sem1 = [c for i, c in enumerate(st.session_state.course_plan[year]) if i < 4 and c]
        sem2 = [c for i, c in enumerate(st.session_state.course_plan[year]) if i >= 4 and c]
        course_data.append({
            "year": year,
            "sem1": ", ".join(sem1),
            "sem2": ", ".join(sem2)
        })

    # Generate HTML using Jinja2 template
    timestamp = datetime.datetime.now().strftime("%B %d, %Y – %I:%M %p")
    template_str = """
    <html>
    <head><style>
        body { font-family: Arial; margin: 40px; }
        h1 { font-size: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #999; padding: 8px; text-align: left; }
    </style></head>
    <body>
        <h1>Course Plan for {{ student_name }}</h1>
        <p><em>Printed: {{ timestamp }}</em></p>
        <table>
            <tr><th>Year</th><th>Semester 1 Courses</th><th>Semester 2 Courses</th></tr>
            {% for row in data %}
            <tr><td>{{ row.year }}</td><td>{{ row.sem1 }}</td><td>{{ row.sem2 }}</td></tr>
            {% endfor %}
        </table>
        <p style='margin-top: 40px;'>Graduation Pathway Summary: (Coming soon)</p>
    </body>
    </html>
    """

    template = Template(template_str)
    html_content = template.render(student_name=student_name or "(Unnamed Student)", data=course_data, timestamp=timestamp)

    # Convert to PDF using pdfkit (ensure wkhtmltopdf is installed)
    pdf_bytes = pdfkit.from_string(html_content, False)
    st.download_button("📥 Download PDF", pdf_bytes, file_name="WHS_Course_Schedule.pdf", mime="application/pdf")

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
            label = f"{year} - {department}"

            if i < 4:
                dept_courses = base_courses[base_courses["Department"] == department]
                eligible_courses = dept_courses[dept_courses["Course Code"].astype(str).apply(
                    lambda code: has_prereq_met(code, year, st.session_state.course_plan_codes, prereq_dict, i)
                )]
            else:
                all_departments = sorted(base_courses["Department"].dropna().unique())
                dept_key = f"{year}_dept_{i}"

                # Attempt to infer department from selected course if dept_key is unset
                selected_name = st.session_state.course_plan[year][i]
                inferred_dept = ""
                if selected_name:
                    match_row = base_courses[base_courses["Course Name"] == selected_name]
                    if not match_row.empty:
                        inferred_dept = match_row.iloc[0]["Department"]

                default_dept = st.session_state.get(dept_key, inferred_dept)

                selected_dept = st.selectbox(
                    f"Select Department ({department})",
                    [""] + all_departments,
                    index=([""] + all_departments).index(default_dept) if default_dept in all_departments else 0,
                    key=dept_key
                )

                if selected_dept:
                    dept_courses = base_courses[base_courses["Department"] == selected_dept]
                    eligible_courses = dept_courses[dept_courses["Course Code"].astype(str).apply(
                        lambda code: has_prereq_met(code, year, st.session_state.course_plan_codes, prereq_dict, i)
                    )]
                else:
                    eligible_courses = pd.DataFrame(columns=base_courses.columns)

            if not eligible_courses.empty:
                options = ["" ] + eligible_courses["Course Name"].tolist()
                code_lookup = dict(zip(eligible_courses["Course Name"], eligible_courses["Course Code"].astype(str)))
                notes_lookup = dict(zip(eligible_courses["Course Name"], eligible_courses["Notes"]))
                selected_course = st.selectbox(
                    label=label,
                    options=options,
                    index=options.index(st.session_state.course_plan[year][i]) if st.session_state.course_plan[year][i] in options else options.index("") if "" in options else 0,
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
