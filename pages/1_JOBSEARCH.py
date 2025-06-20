import os
import sys
import pandas as pd
import streamlit as st
import time
import functions
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
label_text="DAYS SINCE JOB POSTED (DEFAULT: 1, TODAY:0)"
posted_days=st.sidebar.number_input(min_value=0,max_value=60,value=1,label=label_text)

all_jobs=functions.job_search(days_posted=posted_days,host=host,email=email,USAJOB_API_KEY=usajobapi)

raw_df=functions.get_job_info_df(all_jobs)

#debug
debug=True
if debug:st.dataframe(raw_df.head(5))

#temp_df
temp_df=raw_df.copy()


filter_list=[]



#select a state
states=sorted(temp_df['State'].unique())
state=st.sidebar.selectbox('SELECT STATE',options=states,index=None)
if state:temp_df=temp_df.query('State == @state');filter_list.append(state)

#select jobtitle
job_titles=sorted(temp_df['PositionTitle'].unique())
job=st.sidebar.selectbox('SELECT JOB TITLE',options=job_titles,index=None)
if job:temp_df=temp_df.query('PositionTitle == @job');filter_list.append(job)

#department
department=sorted(temp_df['Department'].unique())
department=st.sidebar.selectbox('SELECT DEPARTMENT',options=department,index=None)
if department:temp_df=temp_df.query('Department == @department');filter_list.append(department)

#posted_date
posted_date=sorted(temp_df['PostedDate'].unique())
posted=st.sidebar.selectbox('SELECT POSTED DATE',options=posted_date,index=None)
if posted:temp_df=temp_df.query('PostedDate == @posted');filter_list.append(posted)

#end_date
end_date=sorted(temp_df['EndDate'].unique())
end=st.sidebar.selectbox('SELECT END DATE',options=end_date,index=None)
if end:temp_df=temp_df.query('EndDate == @end');filter_list.append(end)

#end_date
security_clearence=sorted(temp_df['SecurityClearance'].unique())
security=st.sidebar.selectbox('SELECT SECURITY TYPE',options=security_clearence,index=None)
if security:temp_df=temp_df.query('SecurityClearance == @security');filter_list.append(security)

#hiring path
hiring_path=sorted(temp_df['HiringPath'].unique())
hiring=st.sidebar.selectbox('SELECT HIRING TYPE',options=hiring_path,index=None)
if hiring:temp_df=temp_df.query('HiringPath == @hiring');filter_list.append(hiring)


#remote
#remote=sorted(temp_df['SecurityClearance'].unique())
remote=st.sidebar.checkbox('REMOTE JOB')
if remote:temp_df=temp_df.query('Remote == @remote');filter_list.append(remote)

filter_list.append(posted_days)
st.write(f"Filter: {filter_list}")

st.sidebar.write(f"TOTAL JOBS: {len(temp_df)}")


#show the latitude and longitude of the location in the map
loc_df=temp_df[['Latitude','Longitude']]
loc_df=loc_df.rename(columns={'Latitude':'latitude','Longitude':'longitude'})


#pydeck map
# #layer
# layer=pdk.Layer(
#     'ScatterplotLayer',
#     data=temp_df,
#     get_position='[Latitude,Longitude]',
#     get_fill_color='[180,0,200,140]',
#     get_radius=100,
#     pickable=True
# )

# # Tooltip configuration
# tooltip = {
#     "html": "<b>Job Title:</b> {PositionTitle} <br/>"
#             "<b>StartDate:</b> {StartDate} <br/>"
#             "<b>EndDate:</b> {EndDate}",
#     "style": {
#         "backgroundColor": "white",
#         "color": "black"
#     }
# }

# # View settings
# view_state = pdk.ViewState(
#     latitude=temp_df['Latitude'].mean(),
#     longitude=temp_df['Longitude'].mean(),
#     zoom=3
# )

# Show map
# st.pydeck_chart(pdk.Deck(
#     layers=[layer]w

#     initial_view_state=view_state,
#     tooltip=tooltip
# ))
#st.map(loc_df)

#apply function to rows to get the job information

# Initialize map at the average location
m = folium.Map(
    #location=[temp_df['Latitude'].mean(), temp_df['Longitude'].mean()],
    zoom_start=2
)

# Add markers for each job
for _, row in temp_df.iterrows():
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
st_data = st_folium(m, use_container_width=True, height=800)


if debug:st.dataframe(loc_df)





if debug:st.dataframe(temp_df)

show_job=st.sidebar.checkbox("JOB DETAILS AND ⬇️ ")
#change the css feature of the button
st.markdown("""
    <style>
    div.stButton > button[kind="secondary"] {
        background-color: #4CAF50; /* Green */
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        border: none;
        font-weight: bold;
    }
    div.stDownloadButton > button {
        background-color: #007ACC;  /* Blue */
        color: white;
        border-radius: 8px;
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


    # with st.container():
    #     with open(pdf_path, "rb") as f:
    #         st.download_button(
    #             label="⬇️ Download Job Description as PDF",
    #             data=f,
    #             file_name=filename,
    #             mime="application/pdf",
    #             key=f"download_{row['JobID']}"
    #         )
    #     st.markdown(
    #         f"""
    #         <div style='width: 100%; padding: 15px; background-color: #f8f8f8;
    #                     border: 1px solid #ddd; border-radius: 8px; margin-bottom: 0px;'>
    #             <div style="display: flex; justify-content: flex-end;">
    #                 <span style="font-weight: bold;">⬇️ Download button here</span>
    #             </div>
    #             {job_html}
    #         </div>
    #         """,
    #         unsafe_allow_html=True
    #     )

    #     # with open(pdf_path, "rb") as f:
    #     #     st.download_button(
    #     #         label="⬇️ Download Job Description as PDF",
    #     #         data=f,
    #     #         file_name=filename,
    #     #         mime="application/pdf",
    #     #         key=f"download_{row['JobID']}"
    #     #     )


    # # download button in Streamlit
    # with st.container():
    #     # with open(pdf_path, "rb") as f:
    #     #     st.download_button(
    #     #         label="📄 Download Job Description as PDF",
    #     #         data=f,
    #     #         file_name=filename,
    #     #         mime="application/pdf"
    #     #     )

    #     st.markdown(
    #         f"""
    #         <div style='width: 100%; padding: 15px; background-color: #f8f8f8;
    #                     border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px;'>
    #             {job_html}
    #         </div>
    #         """,
    #         unsafe_allow_html=True
    #     )
    #     with open(pdf_path, "rb") as f:
    #         st.download_button(
    #             label="📄 Download Job Description as PDF",
    #             data=f,
    #             file_name=filename,
    #             mime="application/pdf"
    #         )

    
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
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️  Download PDF",
                    data=f,
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_{row['JobID']}"
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
