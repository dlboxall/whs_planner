# WHS\_planner

**WHS\_planner** is a Streamlit-based interactive web app designed to help students at WHS (Watertown High School) plan their 4-year high school course schedules. The planner ensures that students meet core graduation requirements and helps them explore multiple graduation pathways, such as University-bound, Career & Technical Education (CTE), and Advanced/Honors Endorsement tracks.

![WHS Planner Banner](./Banner.png)

## 🚀 Features

* 📅 **Interactive 4-Year Course Plan Entry**
  Students select courses by grade level, organized by department, from a curated catalog.

* 🎓 **Graduation Pathway Guidance**
  The app checks course selections against the requirements for different graduation endorsements:

  * Standard Graduation
  * Career & Technical Endorsement
  * Advanced/Honors Endorsement
  * University/Scholarship Pathways

* ✅ **Requirement Tracking**
  Visual indicators show which requirements are satisfied and which are still unmet.

* 🖨️ **PDF Export**
  Generates a polished printable plan with:

  * WHS logo (small and left-aligned)
  * Student's name and timestamp
  * Course table (by grade and type)
  * Graduation pathway summary

## 📂 Project Structure

```
├── .devcontainer/          # Dev container config (for VSCode)
├── Banner.png              # Banner image (optional)
├── WHS_logo2.webp          # Logo for print export
├── WHS_course_catalog.csv  # CSV file containing available courses
├── WHS_course_plan.py      # Streamlit app main entry point
├── layout.py               # Layout and formatting for Streamlit app
├── requirements.txt        # Python dependencies
├── README.md               # You're reading it!
```

## ⚙️ Getting Started

### Prerequisites

* Python 3.9+
* pip

### Installation

1. Clone the repo:

   ```bash
   git clone https://github.com/yourusername/WHS_planner.git
   cd WHS_planner
   ```

2. (Optional) Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:

   ```bash
   streamlit run WHS_course_plan.py
   ```

## 📌 Customization

* To update the course catalog, edit `WHS_course_catalog.csv`.
* To change layout or print behavior, modify `layout.py`.

## 🧩 Future Enhancements

* Save/load individual student plans
* Admin view for counselors
* Course recommendation engine
* Multiple school support

## 🙋‍♀️ Maintainer

Built and maintained by [@dlboxall](https://github.com/dlboxall).
Have suggestions or want to contribute? Open an issue or submit a pull request!

---
