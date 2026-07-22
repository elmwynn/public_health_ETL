from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db_client import DatabaseClient

class PipelineLogger:
    """
    A class to manage logging for the ETL process.

    :log_id: The id of the current pipeline run
    :api_id: The id of the api being called
    :db_client: The DatabaseClient object
    """
    

    def __init__(self, db_client: 'DatabaseClient', api_id):
        self.db_client = db_client
        self.api_id = api_id 
        self.log_id = None


    def create_ETL_log(self, data:dict = None):
        """
        Create the log entry for the pipeline run
        """
        if data is None:
            data = {}
        defaults = {
            'api_id': self.api_id,
            'status_code' : 1,
            'started_at': datetime.now(),
            'last_heartbeat': datetime.now()
        }
        merged_data = defaults | data
        #insert the log item and set the log_id
        result = self.db_client.single_insert(merged_data, 'etl_run_log', 'config')
        self.log_id = result['data']  

    def update_ETL_log(self, data:dict = None, is_completed:bool = False):
        """
        Update the log entry for the pipeline run
        """
        if data is None:
            data = {}
        data['last_heartbeat'] = datetime.now()
        if is_completed:
            data['completed'] = datetime.now() 
        self.db_client.single_update(data, 'etl_run_log', self.log_id, 'config')

    
    def determine_ETL_endstate(self, data):
        """
        Determine endstate of the pipeline run... should I even use this?
        """
        pass
