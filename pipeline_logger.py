

class PipelineLogger:
    """
    A class to manage logging for the ETL process.
    """
    log_id = None
    api_id = None
    connection = None
    

    def __init__(self, connection, api_id):
        self.connection = connection
        self.api_id = api_id
        pass


    def create_ETL_log(self, data):
        """
        Create the log entry for the pipeline run
        """
        self.log_id = self.connection.single_insert(self, )
        pass   

    def update_ETL_log(data):
        pass 

    
    def determine_ETL_endstate(data):
        pass
