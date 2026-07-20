from datetime import datetime

class PipelineLogger:
    """
    A class to manage logging for the ETL process.

    :log_id: The id of the current pipeline run
    :api_id: The id of the api being called
    :db_client: The DatabaseClient object
    """
    log_id = None
    api_id = None
    db_client = None
    

    def __init__(self, db_client, api_id):
        self.db_client = db_client
        self.api_id = api_id 


    def create_ETL_log(self, data = {}):
        """
        Create the log entry for the pipeline run
        """
        defaults = {
            'api_id': self.api_id,
            'status_code' : 1,
            'started_at': datetime.now(),
            'last_heartbeat': datetime.now()
        }
        merged_data = defaults | data
        #insert the log item and set the log_id
        self.log_id = self.db_client.single_insert(merged_data, )
           

    def update_ETL_log(self, data = {}):
        """
        Update the log entry for the pipeline run
        """
        defaults = {
            'last_heartbeat': datetime.now()
        }
        merged_data = defaults | data
        self.db_client.single_update
        pass 

    
    def determine_ETL_endstate(data):
        pass
