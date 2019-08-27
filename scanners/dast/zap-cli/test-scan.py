from zapv2 import ZAPv2 as ZAP #import ZAP library
import time

apikey = 'tmr' # Change to match the API key set in ZAP, or use None if the API key is disabled


zap = ZAP(apikey=apikey, proxies = {'http': 'http://localhost:8080', 'https': 'http://localhost:8080'})
#setting the local ZAP instance that is open on your local system

target_site = 'http://demo.testfire.net'

zap.urlopen(target_site)
#opens up the the target site. Makes a single GET request

spider_id = zap.spider.scan(target_site)
#this line of code kicks off the ZAP Default Spider. This returns an ID value for the spider

print("Spider ID for the initiated spider scan is: {0}".format(spider_id))


#now we can start monitoring the spider's status
while int(zap.spider.status(spider_id)) < 100:
    print("Current Status of ZAP Spider: {0}%".format(zap.spider.status(spider_id)))
    time.sleep(4)
