import streamlit as st
st.set_page_config(
    page_title="USA JOB SEARCH APP",
    page_icon="",
    layout="wide",         # 👈 This makes it full-width
    initial_sidebar_state="auto"
)

intro_html = """
<div style="font-family: 'Times New Roman', sans-serif; padding: 30px; background-color: #f7f9fa; border-radius: 10px;">
    <h2 style="color: #003366;">📌 Welcome to the Government Job Finder</h2>
    <p>This Streamlit app helps you explore and track U.S. government job opportunities using data from the 
    <a href="https://www.usajobs.gov" target="_blank" style="color: #1a73e8;">USAJobs.gov</a> API.</p>
    <hr>
    <h3 style="color: #2c3e50;">📂 OVERVIEW</h3>
    <ul style="line-height: 1.6;">
        <li>This application provides real-time access to federal job data.</li>
        <li>It uses filters and mapping tools to enhance job discovery.</li>
        <li>Jobs can be saved as PDF and accessed later.</li>
    </ul>

<h3 style="color: #2c3e50;">🔎 JOBSEARCH</h3>
    <ul style="line-height: 1.6;">
        <li>Filter by:
            <ul>
                <li>Days since posted</li>
                <li>State</li>
                <li>Job Title</li>
                <li>Department</li>
                <li>Posted Date & End Date</li>
                <li>Security Type</>
                <li>Hiring Type</>
            </ul>
        </li>
        <li>Search results are displayed on a map hovering over which gives Job Information (Job Title, Posted Date, End Date).</li>
    </ul>



<h3 style="color: #2c3e50;">🛠️ FUNCTIONS</h3>
    <ul style="line-height: 1.6;">
        <li><strong>Interactive Map:</strong> View job locations on a map.</li>
        <li><strong>Job Details:</strong> Click to see full job description.</li>
        <li><strong>Save as PDF:</strong> Export job info to PDF.</li>
        <li><strong>Apply Link:</strong> Open USAJobs application link.</li>
    </ul>

<p style="margin-top: 20px; font-style: italic; color: #555;">
        👉 Start with JOB SEARCH in the sidebar to find opportunities that match your interests.
    </p>
</div>
"""

st.markdown(intro_html, unsafe_allow_html=True)

