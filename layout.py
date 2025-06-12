
import streamlit as st
import pandas as pd

def department_sidebar():
    with st.sidebar:
        with st.expander("Department Codes"):
            dept_codes = {
                "Business": "BUS",
                "Computer Science": "CSC",
                "CTE": "CTE",
                "English": "ENG",
                "Fine Arts and Vocal Music": "MUS",
                "Mathematics": "MTH",
                "Performing Arts": "DRM",
                "Physical Education": "PED",
                "Science": "SCI",
                "Social Studies": "SOC",
                "Visual Arts": "ART",
                "World Languages": "WLG"
            }
            df = pd.DataFrame(dept_codes.items(), columns=["Department", "Code"])
            st.dataframe(df, use_container_width=True, hide_index=True)
