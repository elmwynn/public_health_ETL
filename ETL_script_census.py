from db_conn import connection_object
from ETL_logger import ETL_logger

class ETL_census:
    """
    A class to manage the ETL process for Census data.
    """
    connection = None
    logger = None
    
    def __init__(self):
        self.connection = connection_object()
        self.logger = ETL_logger(self.connection)
        pass
  
    ### PARAMETERS PASSED ###
   

    







    ## DB INTERACTION FUNCTIONS ##










    def run_census_ETL(type = None, year = None, ):
        """
        Run the Census ETL process.
        """
        pass


    
    
