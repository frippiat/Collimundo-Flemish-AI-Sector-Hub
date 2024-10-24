import requests
from datetime import datetime, timedelta
import json
import xmltodict
import os
import time

def payload_SOAP(days,word):
    # Calculate start and end dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")
    word = "sustainability"
    # Construct the SOAP payload
    payload = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fris="http://fris.ewi.be/" xmlns:crit="http://fris.ewi.be/criteria">
       <soapenv:Header/>
       <soapenv:Body>
          <fris:getResearchOutput>
             <crit:researchOutputCriteria>
                <crit:window>
                    <crit:pageSize>10</crit:pageSize>
                    <crit:pageNumber>1</crit:pageNumber>
                    <crit:orderings>
                        <crit:order>
                            <crit:id>entity.created</crit:id>
                            <crit:locale>nl_BE</crit:locale>
                            <crit:direction>DESCENDING</crit:direction>
                        </crit:order>
                    </crit:orderings>
                    <crit:search>
                        <crit:search>{word}</crit:search>
                        <crit:locale>nl_BE</crit:locale>
                    </crit:search>
                </crit:window>
                <crit:dataProviders negated="true">
                   <crit:identifier>test_KUL</crit:identifier>
                </crit:dataProviders>
               <crit:publicationDate>
                   <crit:start>{start_date_str}</crit:start>
                   <crit:end>{end_date_str}</crit:end>
                </crit:publicationDate>
             </crit:researchOutputCriteria>
          </fris:getResearchOutput>
       </soapenv:Body>
    </soapenv:Envelope>"""
    
    return payload

def getResearch(days,word):
    url = "https://app-testing.r4.researchportal.be/ws/ResearchOutputService"
    headers = {
      'Content-Type': 'text/xml; charset=utf-8',
      'Cookie': 'JSESSIONID=BBEC39FA4ED6ACCCB20988C6A5BBBA76'
    }
    payload = payload_SOAP(days,word)
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text




relative_path = "data_fris_research"
script_dir = os.path.dirname(__file__)
output_path = os.path.join(script_dir, relative_path)

os.makedirs(output_path, exist_ok=True)

# Save research outputs for "sustainability"
search_query_sustainability = "sustainability"
research_sustainability_7 = getResearch(92, search_query_sustainability)
today_date = datetime.now().strftime("%m_%d")
file_name_sustainability = f"output_research_sustainability_{today_date}.json"
with open(os.path.join(output_path, file_name_sustainability), "w") as json_file:
    json.dump(xmltodict.parse(research_sustainability_7), json_file, indent=4)
print(f"JSON data saved as {os.path.join(output_path, file_name_sustainability)}")

# Save research outputs for "Artificial Intelligence"
search_query_ai = "Artificial Intelligence"
research_ai_7 = getResearch(100, search_query_ai)
file_name_ai = f"output_research_ai_{today_date}.json"
with open(os.path.join(output_path, file_name_ai), "w") as json_file:
    json.dump(xmltodict.parse(research_ai_7), json_file, indent=4)
print(f"JSON data saved as {os.path.join(output_path, file_name_ai)}")
time.sleep(3)


