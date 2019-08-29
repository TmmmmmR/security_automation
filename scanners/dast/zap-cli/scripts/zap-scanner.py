#!/usr/bin/env python

"""zap-scanner.py: Scans a project given a Web application URL"""

__author__      = "Abdessamad TEMMAR"
__copyright__   = "Copyright 2019, Amundi-ITS"

from zapv2 import ZAPv2
from subprocess import Popen
import os
from time import sleep
import requests
from datetime import datetime
import argparse


zap = ZAPv2(proxies={'http': 'http://localhost:8090', 'https': 'http://localhost:8090'})

def start_zap_spider(baseUrl):
    try:
        scan_id = zap.spider.scan(baseUrl)
        return {"spider_id": scan_id, "message": "Spider Successfully Started"}
    except:
        return "ERROR: Failed to start Scan"

def get_spider_status(spider_id):
    return zap.spider.status(spider_id)

def start_zap_active_scan(baseUrl, scan_policy):
    try:
        scan_id = zap.ascan.scan(baseUrl, scanpolicyname=scan_policy)
        return {"scan_id": scan_id, "message": "Scan Successfully Started"}
    except:
        return "ERROR: Failed to start Scan"

def get_ascan_status(scan_id):
    return zap.ascan.status(scanid=scan_id)

def write_json_report(fullpath, export_format, report_title, report_author, report_time):
    url = 'http://localhost:{0}/JSON/exportreport/action/generate/'.format(os.getenv("ZAP_PORT", 8080))
    export_path = fullpath
    extension = export_format
    report_time = datetime.now().strftime("%I:%M%p on %B %d, %Y")
    source_info = '{0};{1};RSI Team;{2};{3};v1;v1;{4}'.format(report_title, report_author, report_time, report_time)
    alert_severity = 't;t;t;t'  # High;Medium;Low;Info
    alert_details = 't;t;t;t;t;t;t;t;t;t'  # CWEID;#WASCID;Description;Other Info;Solution;Reference;Request Header;Response Header;Request Body;Response Body
    data = {'absolutePath': export_path, 'fileExtension': extension, 'sourceDetails': source_info,
            'alertSeverity': alert_severity, 'alertDetails': alert_details}

    r = requests.post(url, data=data)
    if r.status_code == 200:
        return "Successfully written to target path: {0}".format(export_path)
    else:
        raise Exception("Unable to generate report")

def kill_zap():
	zap.core.shutdown()
	return "ZAP has been shutdown"


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
        parser.add_argument('--url', help='Application URL', required=True)
        parser.add_argument('--token', help='OWASP ZAP API Token', required=True)
        parser.add_argument('--scan_mode', help='OWASP ZAP Scanning mode', required=False, default="Light")
        parser.add_argument('--report_full_path', help='Full path of report', required=True)
        parser.add_argument('--report_export_format', help='Report format (HTML, JSON or XML)', required=True)
        args = parser.parse_args()

        # TODO : Add try/catch statement to validate the API key
        zap = ZAP(apikey = args.api, proxies = {'http': 'http://localhost:8080', 'https': 'http://localhost:8080'})

        echo 'Running OWASP ZAP against {0}'.format(args.url)
