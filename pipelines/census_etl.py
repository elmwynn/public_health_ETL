from datetime import datetime
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
        self.run_timestamp = datetime.now().strftime('%Y%m%d')
        self.query_template = {}
        self.categories_path = {}
        
  
    def fetch_census_geographies(self, url, year, api_key):
        try:
            if not self.query_template:
                self.query_template = self.db_client.get_rows('geography_types', 'census')['data']
            
            geography_array = []
            
            for geography_type_info in self.query_template:
                response_key = geography_type_info['response_key']
                geo_type_id = geography_type_info['geo_type_id']
                etl_step = f"geographies_{geo_type_id}"
               
                modified_url = url + geography_type_info['query_template'] + '&key=' + api_key
                data = self.blob_storage.fetch_or_retrieve(modified_url, etl_step)

                if data:  
                    headers = data[0] # format: ['column_name_one', 'column_name_two']
                    rows = data[1:] # format: [[value_1, value_2], [value_3, value_4],...]
                    items = [dict(zip(headers, row)) for row in rows]
                    geography_array.extend(
                        dict(
                            geo_id = item[response_key],
                            description = item['NAME'],
                            geo_type_id = geo_type_id,
                            year = year) 
                            for item in items
                         )

            return geography_array
        except Exception as e:
            return []

  

    def fetch_census_subcategories(self, url, year, api_key, select_category = None):
        try:
            delimiter = self.db_client.get_rows('api_settings', 'config', {'api_setting_value' : 'ACS_delimiter'}, 'api_setting_value')['data'][0]['api_setting_value']
            safe_delimiter = re.escape(delimiter)
            #get the endpoint_paths from the table and load into a {category_name : path,...} dictionary
            if not self.categories_path:
                self.categories_path = {category['category']: category['endpoint_path'] for category in self.db_client.get_rows('categories', 'census')['data']}
            categories = [select_category] if select_category else self.categories_path.keys()
            subcategory_array = []
            for category in categories:
                endpoint_path = self.categories_path[category] if self.categories_path[category] else ''
                modified_url = url + endpoint_path + '/groups/' + category + '.json?key=' + api_key
                data = self.blob_storage.fetch_or_retrieve(modified_url, f"subcategories_{category}")

                if data and data.get('variables'):
                    ##Keep estimates and ignore percentages/margins. Also strip the character at the end for the internal identifier   
                    filtered_subcategories = {re.sub(r'[a-zA-Z]+$', '', k): v for k, v in data['variables'].items() if k.endswith('E') and not k.endswith('PE') and k.startswith(category)}
                    for subcategory, values in filtered_subcategories.items():
                        ##Split the label up by the stored delimeter, stripping white space    
                        parts = [part.strip() for part in re.split(safe_delimiter, values['label'])]
                        count_parts = len(parts)
                        ##determine what the in-house label and description will be based on the  length of the split up label
                        label = parts[1] if count_parts > 1 else 'UNCATEGORIZED'
                        description = (' - '.join(parts[2:]) if count_parts > 2 
                                    else parts[1] if count_parts > 1 
                                    else parts[0])
                        
                        subcategory_array.append(dict(
                            category = category,
                            subcategory = subcategory,
                            label = label,
                            description = description,
                            raw_text = values['label'],
                            year = year
                        ))

            return subcategory_array
        except Exception as e:
            return[]
                    




    
    def fetch_census_estimates(self,url, year, api_key, acs_type, select_category = None):
        try:
            if not self.query_template:
                self.query_template = self.db_client.get_rows('geography_types', 'census')['data']

            if not self.categories_path:
                self.categories_path = {category['category']: category['endpoint_path'] for category in self.db_client.get_rows('categories', 'census')['data']}

            estimate_array = []
            categories = [select_category] if select_category else self.categories_path.keys()
            filtered_templates = [row for row in self.query_template if acs_type in row['acs_types'].split(",")]
            for template in filtered_templates:
                for category in categories:
                    endpoint_path = self.categories_path[category] if self.categories_path[category] else ''
                    modified_url = url + endpoint_path + template['query_template'].replace('NAME', f"group({category})") + "&key=" + api_key
                    data = self.blob_storage.fetch_or_retrieve(modified_url, f"estimates_{category}")
                    if data:
                        headers = data[0] # format: ['column_name_one', 'column_name_two']
                        rows = data[1:] # format: [[value_1, value_2], [value_3, value_4],...]
                        items = [dict(zip(headers, row)) for row in rows]
                        for item in items:
                            for identifier, value in item.items():
                                if identifier.endswith('E') and not identifier.endswith('PE') and identifier.startswith(category):
                                    subcategory = re.sub(r'[a-zA-Z]+$', '', identifier)
                                    estimate_array.append(
                                        dict(
                                            subcategory = subcategory,
                                            acs_type = acs_type,
                                            year = year,
                                            estimate = item[f"{subcategory}E"],
                                            margin_of_error = item[f"{subcategory}M"],
                                            geo_id = item[template['response_key']]
                                        ))
            return estimate_array
        except Exception as e:
            return []




    def run_census_ETL(self, year = None, acs_type = None, select_group = None ):
        """
        Run the Census ETL process.
        """
        self.base_url = self.db_client.get_rows('api_info', 'config',{'api_id': self.api_id},'base_url')['data'][0]['base_url']
       
        pass