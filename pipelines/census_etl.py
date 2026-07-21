import pandas as pd
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
        secrets = get_secrets()
        self.db_client = DatabaseClient(secrets)
        self.blob_storage = BlobStorage(secrets, self.api_id)
        self.logger = PipelineLogger(self.db_client, self.api_id)
        

  
    def fetch_census_geographies(self, url, year, api_key):
        pass
  

    def fetch_census_subcategories(self, url, year, api_key, select_group = None):
        pass

    
    def fetch_census_estimates(self,url, year, api_key, acs_type):
        pass


        




    





    def run_census_ETL(self, year = None, acs_type = None, select_group = None ):
        """
        Run the Census ETL process.
        """
        self.base_url = self.db_client.get_rows('api_info', {'api_id': self.api_id},'base_url', 'config')[0]['base_url']
        print(self.base_url)
        pass


    
