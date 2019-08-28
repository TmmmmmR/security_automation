import requests #since we will be making a REST API Call
import os

url = 'http://localhost:8080/JSON/exportreport/action/generate/'
apikey = 'tmr'
export_path = '/tmp/tmr.json'
extension = 'json'
source_info = 'Vulnerability Report for Amundi Suite;Abdessamad TEMMAR;RSI;January 8 2018;January 8 2018;v1;v1;Amundi Suite Scan Report'
alert_severity = 't;t;t;t' #High;Medium;Low;Info
alert_details = 't;t;t;t;t;t;f;f;f;f' #CWEID;#WASCID;Description;Other Info;Solution;Reference;Request Header;Response Header;Request Body;Response Body
data = {'absolutePath': export_path, 'fileExtension': extension, 'sourceDetails': source_info, 'alertSeverity': alert_severity,'alertDetails' : alert_details , 'apikey': apikey}

r = requests.post(url, data = data)
print(r.content)
