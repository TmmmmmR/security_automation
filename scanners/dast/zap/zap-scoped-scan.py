#!/usr/bin/env python

import argparse
import getopt
import json
import logging
import os
import os.path
import subprocess
import sys
from pprint import pprint
import time
from datetime import datetime
from six.moves.urllib.parse import urljoin
from pprint import pprint
from zapv2 import ZAPv2
from zap_common import *


parser = argparse.ArgumentParser()

parser.add_argument('-t',  action='store', dest='target', help='Provide the target to scan - [http://example.com]')
parser.add_argument('-e', action='store', dest='endpoints', help='Provide endpoints file - [http://example.com/api/endpoints.txt]' )
parser.add_argument('-z', action='store', dest='zap_options', help='ZAP command line options e.g. -z "-config aaa=bbb -config ccc=ddd"' )
parser.add_argument('-u', action='store', dest='dojo_url', help='The ip:port of the defect dojo location i.e 192.168.2.23:8000' )
parser.add_argument('-a', action='store', dest='dojo_api_key', help='Defect dojo API key: admin:746d89602a29e1897d6342faf00f63d28334fb9e' )
parser.add_argument('-i', action='store', dest='dojo_engagement_id', help='Engagement id of where to commit the scan results to i.e: 3' )


results = parser.parse_args()

class NoUrlsException(Exception):
    pass


config_dict = {}
config_msg = {}
out_of_scope_dict = {}
min_level = 0

# Scan rules that aren't really relevant, eg the examples rules in the alpha set
blacklist = ['-1', '50003', '60000', '60001']

# Scan rules that are being addressed
in_progress_issues = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
# Hide "Starting new HTTP connection" messages
logging.getLogger("requests").setLevel(logging.WARNING)


def main(argv):

    global min_level
    global in_progress_issues
    cid = ''
    context_file = ''
    target = ''
    port = 0
    zap_alpha = False
    info_unspecified = False
    zap_ip = 'localhost'
    zap_options = results.zap_options
    delay = 0
    timeout = 0
    target = results.target
    endpoints = results.endpoints
    dojo_url = results.dojo_url
    dojo_api_key = results.dojo_api_key
    dojo_engagement_id = results.dojo_engagement_id
    check_zap_client_version()

    if running_in_docker():
        base_dir = '/zap/wrk/'
        
    if target.startswith('http://') or target.startswith('https://'):
        target_url = target
    else:
        # assume its a file
        if not os.path.exists(base_dir + target):
            logging.warning('Target must either start with \'http://\' or \'https://\' or be a local file')
            logging.warning('File does not exist: ' + base_dir + target)
            usage()
            sys.exit(3)
        else:
            target_file = target

    # Choose a random 'ephemeral' port and check its available if it wasn't specified with -P option
    if port == 0:
        port = get_free_port()
    logging.debug('Using port: ' + str(port))

    if running_in_docker():
        try:
            params = [
                      '-addonupdate', 'ascanrules']  # In case we're running in the stable container

            if zap_alpha:
                params.append('-addoninstallall')
                params.append('ascanrules')

            add_zap_options(params, zap_options)

            start_zap(port, params)

        except OSError:
            logging.warning('Failed to start ZAP :(')
            sys.exit(3)

    else:
        # Not running in docker, so start one
        mount_dir = ''
        if context_file:
            mount_dir =  os.path.dirname(os.path.abspath(context_file))

        params = ['-addonupdate']

        if (zap_alpha):
            params.extend(['-addoninstall', 'ascanrules'])
            params.extend(['-addoninstall', 'replacer'])

        add_zap_options(params, zap_options)

        try:
            cid = start_docker_zap('owasp/zap2docker-weekly', port, params, mount_dir)
            zap_ip = ipaddress_for_cid(cid)
            logging.debug('Docker ZAP IP Addr: ' + zap_ip)

        except OSError:
            logging.warning('Failed to start ZAP in docker :(')
            sys.exit(3)

    try:
        zap = ZAPv2(proxies={'http': 'http://' + zap_ip + ':' + str(port), 'https': 'http://' + zap_ip + ':' + str(port)})

        wait_for_zap_start(zap, timeout * 40000)
        print(target)
        print(endpoints)

        #command injection problem i recon
        command = "wget "+endpoints
        os.system(command)

        time.sleep(5)

        zap.urlopen(target)
        
        # Give the sites tree a chance to get updated
        time.sleep(5)

        with open("endpoints.txt", 'r') as f:
            for line in f:
                scanid = zap.spider.scan(line,"","","",True)

                # Give the Spider a chance to start
                time.sleep(5)
                while (int(zap.spider.status(scanid)) < 100):
                    # Loop until the spider has finished
                    print('Spider progress %: {}'.format(zap.spider.status(scanid)))
        
        scanid = zap.ascan.scan(target)
        while (int(zap.ascan.status(scanid)) < 100):
            print 'Scan progress %: ' + zap.ascan.status(scanid)
            time.sleep(1)

        write_report('result.xml', zap.core.xmlreport())
        
        time.sleep(10)

        #command injection problem i recon
        commit_to_dojo = 'curl --request POST --url {0}/api/v1/importscan/ --header \'authorization: ApiKey {1}\' --header \'cache-control: no-cache\' --header \'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW\' --form minimum_severity=Info --form scan_date=2018-05-01 --form verified=False --form file=@result.xml --form tags=Test_automation --form active=True --form engagement=/api/v1/engagements/{2}/ --form \'scan_type=ZAP Scan\''.format(dojo_url, dojo_api_key, dojo_engagement_id)
        os.system(commit_to_dojo)
        
        zap.core.shutdown()

    except IOError as e:
        if hasattr(e, 'args') and len(e.args) > 1:
            errno, strerror = e
            print("ERROR " + str(strerror))
            logging.warning('I/O error(' + str(errno) + '): ' + str(strerror))
        else:
            print("ERROR %s" % e)
            logging.warning('I/O error: ' + str(e))
        dump_log_file(cid)

    except NoUrlsException:
        dump_log_file(cid)

    except:
        print("ERROR " + str(sys.exc_info()[0]))
        logging.warning('Unexpected error: ' + str(sys.exc_info()[0]))
        dump_log_file(cid)

if __name__ == "__main__":
    main(sys.argv[1:])


