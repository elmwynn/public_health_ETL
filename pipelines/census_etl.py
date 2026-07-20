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
        secrets = get_secrets()
        self.db_client = DatabaseClient(secrets)
        self.blob_storage = BlobStorage(secrets, self.api_id)
        self.logger = PipelineLogger(self.db_client, self.api_id)
        

  
    ### PARAMETERS PASSED ###








    









    def run_census_ETL(type = None, year = None, ):
        """
        Run the Census ETL process.
        """
        pass


    

test = CensusETL()    
