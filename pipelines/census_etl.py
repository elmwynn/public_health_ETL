from db_client import DatabaseClient
from blob_storage import BlobStorage
from pipeline_logger import PipelineLogger
from config import get_secrets

class CensusETL:
    """
    A class to manage the ETL process for Census data.
    """
    database_client = None
    blob_storage = None
    logger = None
    api_id = 1
    
    def __init__(self):
        secrets = get_secrets()
        self.database_client = DatabaseClient(secrets)
        self.blob_storage = BlobStorage(secrets, self.api_id)
        self.logger = PipelineLogger(self.database_client, self.api_id)
        pass
  
    ### PARAMETERS PASSED ###







    









    def run_census_ETL(type = None, year = None, ):
        """
        Run the Census ETL process.
        """
        pass


    

test = CensusETL()    
