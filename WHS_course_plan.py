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
                default_dept = st.session_state.get(dept_key, "")
                selected_dept = st.selectbox(f"Select Department ({department})", [""] + all_departments, index=[""] + all_departments.index(default_dept) if default_dept in all_departments else 0, key=dept_key)
                st.session_state[dept_key] = selected_dept
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
