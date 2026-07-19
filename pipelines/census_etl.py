from db_conn import ConnectionObject
from pipeline_logger import PipelineLogger

class CensusETL:
    """
    A class to manage the ETL process for Census data.
    """
    connection = None
    logger = None
    
    def __init__(self):
        self.connection = ConnectionObject()
        self.logger = PipelineLogger(self.connection)
        pass
  
    ### PARAMETERS PASSED ###
   

    







    ## DB INTERACTION FUNCTIONS ##










    def run_census_ETL(type = None, year = None, ):
        """
        Run the Census ETL process.
        """
        pass


    
    
