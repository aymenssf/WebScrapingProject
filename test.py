import pandas as pd
import scrapy
import yaml
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from yaml.loader import SafeLoader
import requests
def get_auth(reqs):
    for req in reqs:
        if 'authorization' in dict(req.headers):
            return dict(req.headers)['authorization']


driver.get('https://outbreak.info/situation-reports?pango=A.4')
# sleep(15)
auth = get_auth(driver.requests)
print(auth)