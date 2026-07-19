

class PipelineLogger:
    """
    A class to manage logging for the ETL process.
    """
    log_id = None
    connection = None
    

    def __init__(self, connection):
        self.connection = connection
        pass


    def create_ETL_log(self, data):
        """
        Create the log entry for the pipeline run
        """
        self.log_id = self.connection.single_insert(self, );
        pass   

    def update_ETL_log(data):
        pass 

