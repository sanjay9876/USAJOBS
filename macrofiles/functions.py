import requests
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import os
from weasyprint import HTML
from datetime import datetime
import re
import pytz
from io import BytesIO


est_timezone=pytz.timezone('US/EASTERN')

@st.cache_data
def job_search(days_posted,host,email,USAJOB_API_KEY):

  url = "https://data.usajobs.gov/api/search"
  params = {
      "DatePosted": days_posted,                  
      "ResultsPerPage": 500,
      "Page": 1
  }

  headers = {
    'Host':host,
    'User-Agent': email,
    'Authorization-Key': USAJOB_API_KEY 
  }

  all_jobs = []

  while True:
      print(f"Fetching page {params['Page']}...")
      response = requests.get(url, headers=headers, params=params)

      if response.status_code != 200:
          print(f"Error {response.status_code}: {response.text}")
          break

      data = response.json()
      jobs = data["SearchResult"]["SearchResultItems"]

      if not jobs:
          print("No more jobs.")
          break

      all_jobs.extend(jobs)
      params["Page"] += 1
      time.sleep(0.5)

  #print(f"Total jobs fetched (last {days_posted} days): {len(all_jobs)}")
  #st.write(f"Total jobs fetched (last {days_posted} days): {len(all_jobs)}")
  return all_jobs


#function to create the data frame
def get_job_info_df(all_jobs):
  if len(all_jobs)<1:
      st.warning("NO JOBS FOUND ! INCREASE THE POSTED DAYS !!")
      st.stop()


  job_data = []

  for job in all_jobs:
      desc = job.get("MatchedObjectDescriptor", {})
      user_area = desc.get("UserArea", {}).get("Details", {})
      loc_info = desc.get("PositionLocation", [{}])[0]
      pay_info = desc.get("PositionRemuneration", [{}])[0]

      job_data.append({
          # Basic
          "JobID": job.get("MatchedObjectId"),
          "PositionID": desc.get("PositionID"),
          "PositionTitle": desc.get("PositionTitle"),
          "JobURI": desc.get("PositionURI"),
          "ApplyURI": desc.get("ApplyURI", [None])[0],

          # Location
          "Location": desc.get("PositionLocationDisplay"),
          "City": loc_info.get("CityName"),
          "State": loc_info.get("CountrySubDivisionCode"),
          "Latitude": loc_info.get("Latitude"),
          "Longitude": loc_info.get("Longitude"),

          # Agency Info
          "Agency": desc.get("OrganizationName"),
          "Department": desc.get("DepartmentName"),

          # Job Type Info
          "JobCategory": desc.get("JobCategory", [{}])[0].get("Name"),
          "JobGrade": desc.get("JobGrade", [{}])[0].get("Code"),
          "PositionScheduleCode": desc.get("PositionSchedule", [{}])[0].get("Code"),
          "PositionOfferingTypeCode": desc.get("PositionOfferingType", [{}])[0].get("Code"),

          # Pay
          "SalaryMin": float(pay_info.get("MinimumRange", 0)),
          "SalaryMax": float(pay_info.get("MaximumRange", 0)),
          "SalaryType": pay_info.get("RateIntervalCode"),
          "SalaryDescription": pay_info.get("Description"),

          # Dates
          "PostedDate": desc.get("PublicationStartDate"),
          "EndDate": desc.get("ApplicationCloseDate"),
          "StartDate": desc.get("PositionStartDate"),
          "PositionEndDate": desc.get("PositionEndDate"),

          # Descriptions
          "JobSummary": user_area.get("JobSummary"),
          "MajorDuties": user_area.get("MajorDuties", [None])[0],
          "QualificationSummary": desc.get("QualificationSummary"),

          # Optional Details
          "Education": user_area.get("Education"),
          "Evaluations": user_area.get("Evaluations"),
          "HowToApply": user_area.get("HowToApply"),
          "WhatToExpectNext": user_area.get("WhatToExpectNext"),
          "RequiredDocuments": user_area.get("RequiredDocuments"),
          "PromotionPotential": user_area.get("PromotionPotential"),
          "Relocation": user_area.get("Relocation"),

          # Contact Info
          "AgencyEmail": user_area.get("AgencyContactEmail"),
          "AgencyPhone": user_area.get("AgencyContactPhone"),

          # Eligibility & Access
          "HiringPath": ", ".join(user_area.get("HiringPath", [])),
          "KeyRequirements": ", ".join(user_area.get("KeyRequirements", [])),
          "SecurityClearance": user_area.get("SecurityClearance"),
          "TeleworkEligible": user_area.get("TeleworkEligible"),
          "Remote": user_area.get("RemoteIndicator"),
          "FinancialDisclosure": user_area.get("FinancialDisclosure"),
          "BargainingUnitStatus": user_area.get("BargainingUnitStatus"),

          # Meta
          "TotalOpenings": user_area.get("TotalOpenings"),
          "WithinArea": user_area.get("WithinArea"),
          "CommuteDistance": user_area.get("CommuteDistance"),
          "ServiceType": user_area.get("ServiceType"),
          "AnnouncementClosingType": user_area.get("AnnouncementClosingType"),

          # Benefits
          "Benefits": user_area.get("Benefits"),
          "BenefitsUrl": user_area.get("BenefitsUrl"),
          "BenefitsDisplayDefaultText": user_area.get("BenefitsDisplayDefaultText")
      })

  # Create DataFrame
 
  df = pd.DataFrame(job_data)
  df.fillna('N/A',inplace=True)
  df=df.map(lambda x:'N/A' if x is None else x)

  #change the date format
  date_columns=['PostedDate','EndDate','StartDate','PositionEndDate']

  for date in date_columns:
       
       df[date]=pd.to_datetime(df[date]).apply(lambda x:x.strftime('%Y-%m-%d'))
  

  return df


#create the html page
def render_job_html(row):
    def format_text(text):
        return str(text).replace("\n", "<br>") if text and text != "N/A" else "N/A"

    summary = format_text(row['JobSummary'])
    education = format_text(row['Education'])
    duties = format_text(row['MajorDuties'])
    qualifications = format_text(row['QualificationSummary'])
    evaluations=format_text(row['Evaluations'])
    whattoexpect=format_text(row['WhatToExpectNext'])
    requiredocs=format_text(row['RequiredDocuments'])
    how_to_apply = format_text(row['HowToApply'])
    salary_desc = (
        f"${row['SalaryMin']:,.0f} - ${row['SalaryMax']:,.0f} {row['SalaryType']}"
        if row['SalaryMin'] != "N/A" else "N/A"
    )

    html = f"""
        <div style="width: 100%; font-family: Arial; font-size: 14px; line-height: 1.6; padding: 5px;">
        <p><b>Job Title:</b> {row['PositionTitle'].upper()}</p>
        <b>Agency:</b> {row['Agency']}<br>
        <b>Department:</b> {row['Department']}<br>
        <b>Location:</b> {row['Location']} ({row['City']}, {row['State']})<br>
        <b>Posted:</b> {row['PostedDate']} &nbsp;|&nbsp; <b>Closes:</b> {row['EndDate']}<br>
        <b>Salary:</b> {salary_desc}<br>
        <b>Schedule:</b> {row['PositionScheduleCode']} &nbsp;|&nbsp;
        <b>Type:</b> {row['PositionOfferingTypeCode']}<br>
        <b>Grade:</b> {row['JobGrade']} &nbsp;|&nbsp;
        <b>Category:</b> {row['JobCategory']}<br>
        <b>Hiring Path:</b> {row['HiringPath']}<br>
        <b>Security Clearance:</b> {row['SecurityClearance']}<br>
        <b>Remote Eligible:</b> {row['Remote']}<br>
        <hr style="margin: 0.5em 0;">
        <p style='text-align: justify;'><b>Summary:</b><br>{summary}</p>
        <p style='text-align: justify;'><b>Education:</b><br>{education}</p>
        <p style='text-align: justify;'><b>Major Duties:</b><br>{duties}</p>
        <p style='text-align: justify;'><b>Qualifications:</b><br>{qualifications}</p>
        <p style='text-align: justify;'><b>Evaluations:</b><br>{evaluations}</p>
        <p style='text-align: justify;'><b>WhatToExpectNext:</b><br>{whattoexpect}</p>
        <p style='text-align: justify;'><b>Requirements:</b><br>{requiredocs}</p>
        <p style='text-align: justify;'><b>How to Apply:</b><br>{how_to_apply}</p>
        <b>Contact:</b> {row['AgencyEmail']} | {row['AgencyPhone']}<br>
        <b><a href="{row['ApplyURI']}" target="_blank">Apply Here</a></b></div>
    """
    return html

def save_job_as_pdf(html_content, filename="job_description.pdf"):
    # Add printed date at the top
    printed_date = f'{datetime.now(est_timezone).strftime("%Y-%m-%d, %H:%S")}'
    header = f"""
    <div style="text-align: right; font-size: 10px; margin-bottom: 20px;">
        created on: {printed_date}
    </div>
    """
   
    # Create in-memory PDF
    pdf_buffer = BytesIO()
    full_html=header+html_content
    HTML(string=full_html).write_pdf(target=pdf_buffer)
    pdf_buffer.seek(0)  # Move to the beginning of the file


    return pdf_buffer


def clean_filename(filename):
    # Remove invalid characters for all OSes
    return re.sub(r'[\\/*?:"<>|]', "_", filename)



def show_clock():
    html_code = """
    <div style="
        position: fixed;
        top: 10px;
        right: 20px;
        background-color: black;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        color: limegreen;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        z-index: 1000;
        font-family: monospace;"
        id="clock">
    </div>

    <script>
      function updateTime() {
        const clockElement = document.getElementById('clock');
        const now = new Date();
        const timeStr = now.toLocaleTimeString();
        const dayName = now.toLocaleDateString('en-US', { weekday: 'long' });
        const dateStr = now.toLocaleDateString('en-US');
        clockElement.textContent = `🕒 ${timeStr}, ${dayName}, ${dateStr}`;
      }
      setInterval(updateTime, 1000);
      updateTime();
    </script>
    """
    components.html(html_code, height=0, width=0)




