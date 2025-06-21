import os
import sys
import pandas as pd
import streamlit as st
import time
import macrofiles.functions as functions
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime

#import pydeck as pdk

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
label_text="DAYS SINCE JOB POSTED (DEFAULT: 1)"
posted_days=st.sidebar.number_input(min_value=1,max_value=60,value=1,label=label_text)

all_jobs=functions.job_search(days_posted=posted_days,host=host,email=email,USAJOB_API_KEY=usajobapi)

raw_df=functions.get_job_info_df(all_jobs)

#debug
debug=False
if debug:st.dataframe(raw_df.head(5))

#temp_df
temp_df=raw_df.copy()


filter_list=[]
info_dict={}
info_dict['posted_days']=posted_days



#select a state
states=sorted(temp_df['State'].unique())
state=st.sidebar.selectbox('SELECT STATE',options=states,index=None)
if state:temp_df=temp_df.query('State == @state');info_dict['state']=state

#select jobtitle
job_titles=sorted(temp_df['PositionTitle'].unique())
job=st.sidebar.selectbox('SELECT JOB TITLE',options=job_titles,index=None)
if job:temp_df=temp_df.query('PositionTitle == @job');info_dict['job_title']=job

#department
department=sorted(temp_df['Department'].unique())
department=st.sidebar.selectbox('SELECT DEPARTMENT',options=department,index=None)
if department:temp_df=temp_df.query('Department == @department');info_dict['department']=department

#posted_date
# if temp_df.empty:
#     st.warning("NO JOBS FOUND !!!")
#     st.stop()
try:
    posted_date=sorted(temp_df['PostedDate'].unique())
except:
    st.warning("NO JOBS FOUND ! REVISIT YOUR SEARCH !")
posted=st.sidebar.selectbox('SELECT POSTED DATE',options=posted_date,index=None)
if posted:temp_df=temp_df.query('PostedDate == @posted');info_dict['posted']=posted

#end_date
end_date=sorted(temp_df['EndDate'].unique())
end=st.sidebar.selectbox('SELECT END DATE',options=end_date,index=None)
if end:temp_df=temp_df.query('EndDate == @end');info_dict['end_date']=end

#end_date
security_clearence=sorted(temp_df['SecurityClearance'].unique())
security=st.sidebar.selectbox('SELECT SECURITY TYPE',options=security_clearence,index=None)
if security:temp_df=temp_df.query('SecurityClearance == @security');info_dict['security_clearance']=security

#hiring path
hiring_path=sorted(temp_df['HiringPath'].unique())
hiring=st.sidebar.selectbox('SELECT HIRING TYPE',options=hiring_path,index=None)
if hiring:temp_df=temp_df.query('HiringPath == @hiring');info_dict['hiring_path']=hiring


#remote
#remote=sorted(temp_df['SecurityClearance'].unique())
remote=st.sidebar.checkbox('REMOTE JOB')
if remote:temp_df=temp_df.query('Remote == @remote');filter_list.append(remote)

#filter_list.append(posted_days)
if debug:st.write(f"Filter: {info_dict}")

if temp_df.empty:
    st.warning("NO JOBS FOUND !!!")
    st.stop()

st.sidebar.write(f"TOTAL JOBS: {len(temp_df)}")


#create the header
header_html = '<div style="margin-bottom: 20px; font-size: 15px; color:blue">YOUR SELECTION\n'
for key, value in info_dict.items():
    header_html += f'  <div><strong style="display: inline-block; width: 150px;">{key.upper()}:</strong> {str(value).upper()}</div>\n'
header_html += '</div>'

st.markdown(header_html,unsafe_allow_html=True)


#show the latitude and longitude of the location in the map
loc_df=temp_df[['Latitude','Longitude']]
loc_df=loc_df.rename(columns={'Latitude':'latitude','Longitude':'longitude'})




#apply function to rows to get the job information

# Initialize map at the average location
m = folium.Map(
    #location=[temp_df['Latitude'].mean(), temp_df['Longitude'].mean()],
    zoom_start=2
)

# Add markers for each job
for index, row in temp_df.iterrows():
    popup_content = f"""
    <b>Job Title:</b> {row['PositionTitle']}<br>
    <b>Posted:</b> {row['PostedDate']}<br>
    <b>End:</b> {row['EndDate']}
    """
    tooltip_text = (
        f"Job: {row['PositionTitle']}\n"
        f"Posted: {row['PostedDate']}\n"
        f"End: {row['EndDate']}"
    )


    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup_content,
        tooltip=tooltip_text
    ).add_to(m)

# Fit map to bounds of all points
bounds = [[temp_df['Latitude'].min(), temp_df['Longitude'].min()],
          [temp_df['Latitude'].max(), temp_df['Longitude'].max()]]
m.fit_bounds(bounds)

# Display map in Streamlit
#st_data = st_folium(m, use_container_width=True, height=800)
with st.spinner("Loading map .."):
  st_data = st_folium(m, use_container_width=True, height=800)


if debug:st.dataframe(loc_df)





if debug:st.dataframe(temp_df)

show_job=st.sidebar.checkbox("JOB DETAILS, DOWNLOAD (⬇️), APPLY")
#change the css feature of the button
st.markdown("""
    <style>
    div.stButton > button[kind="secondary"] {
        background-color: #4CAF50; /* Green */
        color: white;
        border-radius: 6px;
        padding: 8px 16px;
        border: none;
        font-weight: bold;
    }
    div.stDownloadButton > button {
        background-color: #007ACC;  /* Blue */
        color: white;
        border-radius: 6px;
        padding: 0.5em 1em;
        font-weight: bold;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)
#create the job info page
if not show_job:st.stop()
for _, row in temp_df.iterrows():
    time.sleep(0.5)
    #st.markdown(functions.render_job_html(row), unsafe_allow_html=True)
    # Wrap each job block in a full-width container
    job_html = functions.render_job_html(row)

    # create filename with job title and date
    raw_title = row['PositionTitle'].replace(" ", "_")
    job_title=functions.clean_filename(raw_title)

    filename = f"{job_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    # save as PDF
    pdf_path = functions.save_job_as_pdf(job_html, filename)


    
    
    #     st.markdown("---")
    
    with st.container():
        col1, col2 = st.columns([7, 1])

        with col1:
            st.markdown(
                f"""
                <div style='padding: 15px; background-color: #f8f8f8;
                            border: 1px solid #ddd; border-radius: 8px;
                            margin-bottom: 0px;'>
                {job_html}
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
           # with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️  Download PDF",
                data=pdf_path,
                file_name=filename,
                mime="application/pdf",
                key=f"download_{row['JobID']}"
            )

            #want to include apply funciton here
            st.markdown(
                f"""<b><a href="{row['ApplyURI']}" target="_blank" style='text-decoration: none; color: white; 
                background-color: #4CAF50; padding: 8px 16px; border-radius: 6px; display: inline-block;'>
                ✅ Apply This Job  
                </a></b>""",
                 unsafe_allow_html=True
                )


        st.markdown("---")


    # generate HTML content for one job
    #job_html = functions.render_job_html(row)

    # create filename with job title and date
    # raw_title = row['PositionTitle'].replace(" ", "_")
    # job_title=functions.clean_filename(raw_title)
    # filename = f"{job_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    # save as PDF
    #pdf_path = functions.save_job_as_pdf(job_html, filename)

    # # download button in Streamlit
    # with open(pdf_path, "rb") as f:
    #     st.download_button(
    #         label="📄 Download Job Description as PDF",
    #         data=f,
    #         file_name=filename,
    #         mime="application/pdf"
    #     )
