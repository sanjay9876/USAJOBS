import os
import sys
import pandas as pd
import streamlit as st
import functions
import requests
import folium
from streamlit_folium import st_folium
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
label_text="DAYS SINCE JOB POSTED (DEFAULT: 5, TODAY:0)"
posted_days=st.sidebar.number_input(min_value=0,max_value=60,value=5,label=label_text)

all_jobs=functions.job_search(days_posted=posted_days,host=host,email=email,USAJOB_API_KEY=usajobapi)

raw_df=functions.get_job_info_df(all_jobs)

#debug
debug=True
if debug:st.dataframe(raw_df.head(5))

#temp_df
temp_df=raw_df.copy()





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

# # center on Liberty Bell, add marker
# m = folium.Map(location=[39.949610, -75.150282], zoom_start=16)
# folium.Marker(
#     [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
# ).add_to(m)

# # call to render Folium map in Streamlit
# st_data = st_folium(m, width=725)

if debug:st.dataframe(loc_df)





if debug:st.dataframe(temp_df)