from azure.storage.blob import BlobServiceClient
from datetime import datetime
import json


class BlobStorage:

    def __init__(self, secrets, api_id):
        self.secrets = secrets
        self.api_id = api_id
        self.service = None
        self.container = None
        self.e_file_list = None
        self.s_file_list = []
        self.s_file_list_completed = []
        self.connect()
    
    def connect(self):
        """
        Establish a connection with the cloud service client.
        """
        self.service = BlobServiceClient.from_connection_string(self.secrets['BLOB'])
        self.container = self.service.get_container_client('raw-data')       

    def upload_raw(self, etl_step, raw_data):
        """
        Upload raw API data to cloud storage
        """
        try:
            file_key = f"{self.api_id}/{etl_step}_{datetime.now().strftime('%Y%m%d')}.json"
            self.container.upload_blob(file_key, json.dumps(raw_data))
            self.s_file_list.append(file_key)
            return {'success': True, 'data': file_key}
        except Exception as e:
            return {'success': False, 'error': f"File upload for {file_key}_ failed: {e}"}
   

    def download_raw(self, file_key):
        """
        Download specified raw data from cloud storage
        """
        try:
            client = self.container.get_blob_client(f"{file_key}")
            raw_data = json.loads(client.download_blob().readall())
            return {'success':True, 'data': raw_data}
        except Exception as e:
            return {'success':False, 'error': f"Failed to get {file_key}: {e}"}
    
    def get_existing_files(self):
        """
        Get files existing in cloud storage related to the current pipeline
        """
        ##if we haven't fetched the list yet, it'll be None so fetch the list
        if not isinstance(self.e_file_list, list):  
            self.e_file_list = list(self.container.list_blob_names(name_starts_with=f"{self.api_id}/"))
        return self.e_file_list
    
    def is_uploaded_at_start(self, file_key):
        """
        Check if the json has already been uploaded
        """
        if file_key not in self.get_existing_files():
            return False
        return True 

    def is_uploaded_in_session(self, file_key):
        """
        Check if json has already been uploaded in the current pipeline run
        """
        if file_key in self.s_file_list:
            return True
        return False

    def is_completed_in_session(self, file_key):
        """
        Check if pipeline has been completed for that file
        """
        if file_key in self.s_file_list and file_key in self.s_file_list_completed:
            return True
        return False    

    def mark_step_completed(self, file_key):
        """
        Mark the file as completed by adding it to the completed list for the session
        """
        if file_key not in self.s_file_list_completed:
            self.s_file_list_completed.append(file_key)