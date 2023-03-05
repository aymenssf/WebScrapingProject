import pandas as pd
import scrapy
import yaml
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from yaml.loader import SafeLoader
import requests

with open('childs.yml', 'w') as file:
    response = requests.get('https://cov-lineages.org/data/lineages.yml')
    file.write(response.text)


def get_auth(reqs):
    for req in reqs:
        if 'authorization' in dict(req.headers):
            return dict(req.headers)['authorization']


driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://outbreak.info/situation-reports?pango=A.4')
# sleep(15)
auth = get_auth(driver.requests)
driver.close()

# MONGO_HOST = "localhost"
# MONGO_PORT = "27017"
MONGO_DB = "db_cov"
MONGO_USER = 'python'
MONGO_PASS = 'python123'


class VariantsSpider(scrapy.Spider):
    name = 'extractor'

    def __init__(self, auth):
        self.headers = {
            'authorization': auth
        }
        self.df = pd.read_html('https://cov-lineages.org/lineage_list.html')[0]
        self.df['children'] = pd.Series()
        self.df['mutations'] = pd.Series()
        with open('childs.yml', 'r') as f:
            self.config = list(yaml.load_all(f, Loader=SafeLoader))[0]
            self.mutation_template = 'https://api.outbreak.info/genomics/lineage-mutations?pangolin_lineage={' \
                                     '}&frequency=0.75 '

    def start_requests(self):
        for index, row in self.df.iterrows():
            # if index > 5 :
            #      continue
            yield Request(
                self.mutation_template.format(row['Lineage']),
                headers=self.headers,
                meta={
                    'Lineage': row['Lineage'],
                    'index': index
                },
                callback=self.parse_mutations
            )

    def get_children(self, name):
        return [item['name'] for item in self.config if item.get('parent') == name]

    def parse_mutations(self, response):
        try:
            mutations = [mut['mutation'] for mut in response.json()['results'][response.meta['Lineage']]]
        except KeyError:
            mutations = []
        self.df.loc[self.df['Lineage'] == response.meta['Lineage'], 'mutations'] = '\n'.join(mutations)
        self.df.loc[response.meta['index'], 'children'] = '\n'.join(
            self.get_children(self.df.loc[response.meta['index']]['Lineage']))
        item_dict = self.df.loc[response.meta['index']].to_dict()
        yield item_dict

    def close(self, reason):
        self.df.to_excel('output.xlsx')


process = CrawlerProcess({
    # 'LOG_LEVEL': 'ERROR',
    #    'FEED_URI': 'output.csv',
    #   'FEED_FORMAT': 'csv',
    # 'DOWNLOAD_DELAY': 0.25,
    'MONGO_USER': MONGO_USER,
    'MONGO_PASS': MONGO_PASS,
    'MONGO_DB': MONGO_DB,
    'ITEM_PIPELINES': {
        'pipeline.VariantsPipeline': 300
    }
})

process.crawl(VariantsSpider, auth)
process.start()
