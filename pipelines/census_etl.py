import pandas as pd
import requests
import json
import re
from db_client import DatabaseClient
from blob_storage import BlobStorage
from pipeline_logger import PipelineLogger
from config import get_secrets

class CensusETL:
    """
    A class to manage the ETL process for ACS Census data.
    """

    
    def __init__(self):
        self.api_id = 1
        self.base_url = None
        self.secrets = get_secrets()
        self.db_client = DatabaseClient(self.secrets)
        self.blob_storage = BlobStorage(self.secrets, self.api_id)
        self.logger = PipelineLogger(self.db_client, self.api_id)
        self.query_template = {}
        

  
    def fetch_census_geographies(self, url, year, api_key):
        try:
            if not self.query_template:
                self.query_template = self.db_client.get_rows('geography_types', 'census')['data']

            for geography_type_info in self.query_template:
                modified_url = url + geography_type_info['query_template'] + '&key=' + api_key
                response_key = geography_type_info['response_key']
                geo_type_id = geography_type_info['geo_type_id']

                response = requests.get(f"{modified_url}")

                if response.status_code == 200:
                    data = response.json()
                    headers = data[0]
                    rows = data[1:]

                    items = [dict(zip(headers, row)) for row in rows]
                    geography_array = [dict(geo_id= item[response_key], description = item['NAME'], geo_type_id = geo_type_id, year = year) for item in items]
            

            return geography_array
                


        except Exception as e:

            pass
  

    def fetch_census_subcategories(self, url, year, api_key, select_category = None):
        delimiter = self.db_client.get_rows('api_settings', 'config', {'api_setting_value' : 'ACS_delimiter'}, 'api_setting_value')['data'][0]['api_setting_value']
        categories_data =  self.db_client.get_rows('categories', 'census')

        categories = [select_category] if select_category else [category['category'] for category in categories_data]

        for category in categories:
            modified_url = url + categories_data[category]['endpoint_path'] + '/groups/' . category + '.json?key=' + api_key
            response = requests.get(f"{modified_url}")

            safe_delimiter = re.escape(delimiter)

            if response.status_code == 200:
                data = response.json() 
                ##Keep estimates and ignore percentages/margins. Also strip the character at the end for the internal identifier   
                filtered_subcategories = {re.sub(r'[a-zA-Z]+$', '', k): v for k, v in data.items() if k.endswith('E') and not k.endswith('PE') and k.startswith(category)}
                for subcategory in filtered_subcategories:
                    parts = re.split(safe_delimiter, subcategory['label'])
                    parts = [part.strip() for part in parts]


                    pass




    
    def fetch_census_estimates(self,url, year, api_key, acs_type):
        if not self.query_template:
            self.query_template = self.db_client.get_rows('geography_types', 'census')['data']

        pass







    





    def run_census_ETL(self, year = None, acs_type = None, select_group = None ):
        """
        Run the Census ETL process.
        """
        self.base_url = self.db_client.get_rows('api_info', 'config',{'api_id': self.api_id},'base_url')['data'][0]['base_url']
        print(self.base_url)
        pass