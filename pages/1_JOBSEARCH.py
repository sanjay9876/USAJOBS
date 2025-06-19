import os
import sys
import pandas as pd
import streamlit as st
import functions
import requests

st.set_page_config(
    page_title="USA JOB SEARCH APP",
    page_icon="",
    layout="wide",         # 👈 This makes it full-width
    initial_sidebar_state="auto"
)

#usajobapi
usajobapi=os.getenv('usajobapi')
email='bhattathakur2015@gmail.com'
host='data.usajobs.gov'

#job posted days
days=2

all_jobs=functions.job_search(days_posted=days,host=host,email=email,USAJOB_API_KEY=usajobapi)

raw_df=functions.get_job_info_df(all_jobs)

#debug
debug=True
if debug:st.dataframe(raw_df.head(5))

#temp_df
temp_df=raw_df.copy()


#if debug:st.write(f"states: {states}")

#select a state
states=sorted(temp_df['State'].unique())
state=st.sidebar.selectbox('SELECT STATE',options=states,index=None)
if state:temp_df=temp_df.query('State == @state')

#select jobtitle
job_titles=sorted(temp_df['PositionTitle'].unique())
job=st.sidebar.selectbox('SELECT JOB TITLE',options=job_titles,index=None)
if job:temp_df=temp_df.query('PositionTitle == @job')

#department
department=sorted(temp_df['Department'].unique())
department=st.sidebar.selectbox('SELECT DEPARTMENT',options=department,index=None)
if department:temp_df=temp_df.query('Department == @department')

#posted_date
posted_date=sorted(temp_df['PostedDate'].unique())
posted=st.sidebar.selectbox('SELECT POSTED DATE',options=posted_date,index=None)
if posted:temp_df=temp_df.query('PostedDate == @posted')

#end_date
end_date=sorted(temp_df['EndDate'].unique())
end=st.sidebar.selectbox('SELECT END DATE',options=end_date,index=None)
if end:temp_df=temp_df.query('EndDate == @end')

#end_date
security_clearence=sorted(temp_df['SecurityClearance'].unique())
security=st.sidebar.selectbox('SELECT SECURITY TYPE',options=security_clearence,index=None)
if end:temp_df=temp_df.query('SecurityClearance == @security')

#remote
#remote=sorted(temp_df['SecurityClearance'].unique())
remote=st.sidebar.checkbox('REMOTE JOB')
if remote:temp_df=temp_df.query('Remote == @remote')





if debug:st.dataframe(temp_df)