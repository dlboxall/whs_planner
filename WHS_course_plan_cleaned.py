import streamlit as st
from datetime import datetime
from jinja2 import Template
from xhtml2pdf import pisa
import io

# Page configuration
st.set_page_config(page_title="Course Planner", layout="wide")
st.title("📘 High School Course Planner")

# Define student name input
st.session_state["student_name_input"] = st.text_input("Enter Student Name:", value=st.session_state.get("student_name_input", ""))
student_name = st.session_state.get("student_name_input", "(Unnamed Student)")

# Constants
years = ["9th Grade", "10th Grade", "11th Grade", "12th Grade"]
course_catalog = {
    "English 9": {"subject": "Language Arts", "prerequisites": []},
    "English 10": {"subject": "Language Arts", "prerequisites": ["English 9"]},
    "English 11": {"subject": "Language Arts", "prerequisites": ["English 10"]},
    "Algebra I": {"subject": "Mathematics", "prerequisites": []},
    "Geometry": {"subject": "Mathematics", "prerequisites": ["Algebra I"]},
    "Biology": {"subject": "Science", "prerequisites": []},
    "Chemistry": {"subject": "Science", "prerequisites": ["Biology"]},
    "World History": {"subject": "Social Studies", "prerequisites": []},
    "U.S. History": {"subject": "Social Studies", "prerequisites": ["World History"]},
    "Physical Education": {"subject": "Health/PE", "prerequisites": []},
    "Art I": {"subject": "Fine Arts", "prerequisites": []},
    "Band": {"subject": "Fine Arts", "prerequisites": []},
    "Spanish I": {"subject": "Foreign Language", "prerequisites": []},
    "Spanish II": {"subject": "Foreign Language", "prerequisites": ["Spanish I"]},
}

# Graduation summary builder
def build_grad_summary():
    return [
        {"label": "4 Units of Language Arts", "value": "TBD", "met": False},
        {"label": "3 Units of Mathematics", "value": "TBD", "met": False},
        {"label": "3 Units of Science", "value": "TBD", "met": False},
        {"label": "3 Units of Social Studies", "value": "TBD", "met": False},
        {"label": "1 Unit of Health/PE", "value": "TBD", "met": False},
        {"label": "1 Unit of Fine Arts", "value": "TBD", "met": False},
        {"label": "2 Units of Foreign Language or Career Tech", "value": "TBD", "met": False},
        {"label": "Electives to complete 23 total units", "value": "TBD", "met": False},
    ]

# Build course plan UI if not already initialized
if "course_plan" not in st.session_state:
    st.session_state.course_plan = {year: ["" for _ in range(8)] for year in years}

# UI: Course selection
st.subheader("📝 Select Courses")
for year in years:
    st.markdown(f"### {year}")
    cols = st.columns(4)
    for i, col in enumerate(cols):
        idx = i
        with col:
            st.session_state.course_plan[year][idx] = st.selectbox(
                f"Semester 1 - Course {i+1}", [""] + list(course_catalog.keys()),
                key=f"{year}_sem1_{i}", index=course_catalog.keys().__contains__(st.session_state.course_plan[year][idx])
            )
    cols2 = st.columns(4)
    for i, col in enumerate(cols2):
        idx = i + 4
        with col:
            st.session_state.course_plan[year][idx] = st.selectbox(
                f"Semester 2 - Course {i+1}", [""] + list(course_catalog.keys()),
                key=f"{year}_sem2_{i}", index=course_catalog.keys().__contains__(st.session_state.course_plan[year][idx])
            )

# Utility: Build course data

def build_course_data():
    data = []
    for year in years:
        sem1 = [c for i, c in enumerate(st.session_state.course_plan[year]) if i < 4 and c]
        sem2 = [c for i, c in enumerate(st.session_state.course_plan[year]) if i >= 4 and c]
        data.append({"year": year, "sem1": ", ".join(sem1), "sem2": ", ".join(sem2)})
    return data

# Graduation Summary
with st.expander("📊 Graduation Requirements Summary"):
    grad_summary = build_grad_summary()
    for item in grad_summary:
        status = "✅" if item["met"] else "❌"
        st.write(f"{status} {item['label']} ({item['value']})")

# PDF Export Button
if st.button("📄 Export Schedule to PDF"):
    course_data = build_course_data()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    template_str = """
    <html>
    <head><style>
    body { font-family: Arial; }
    h1 { color: #2c3e50; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
    </style></head>
    <body>
    <h1>Course Plan for {{ student_name }}</h1>
    <p><em>Printed: {{ timestamp }}</em></p>
    <table>
    <tr><th>Year</th><th>Semester 1</th><th>Semester 2</th></tr>
    {% for row in course_data %}
    <tr><td>{{ row.year }}</td><td>{{ row.sem1 }}</td><td>{{ row.sem2 }}</td></tr>
    {% endfor %}
    </table>

    <h2>Graduation Summary</h2>
    <table>
    <tr><th>Requirement</th><th>Value</th><th>Met</th></tr>
    {% for item in grad_summary %}
    <tr><td>{{ item.label }}</td><td>{{ item.value }}</td><td>{{ "Yes" if item.met else "No" }}</td></tr>
    {% endfor %}
    </table>
    </body>
    </html>
    """

    template = Template(template_str)
    html_content = template.render(
        student_name=student_name,
        course_data=course_data,
        grad_summary=grad_summary,
        timestamp=timestamp
    )

    pdf_output = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html_content), dest=pdf_output)
    pdf_output.seek(0)
    st.download_button("📥 Download PDF", data=pdf_output, file_name="Course_Plan.pdf", mime="application/pdf")
