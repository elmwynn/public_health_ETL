from azure.storage.blob import BlobServiceClient
from datetime import datetime
import json


class BlobStorage:
   

    def __init__(self, secrets, api_id):
        self.secrets = secrets
        self.api_id = api_id
        self.blob_service = None
        self.blob_container = None
        self.blob_dictionary = None
        self.blob_connect()
        pass
    
    def blob_connect(self):
        try:
            self.blob_service = BlobServiceClient.from_connection_string(self.secrets['BLOB'])
            self.blob_container = self.blob_service.get_container_client('raw-data')
            print("Successfully connected to Blob Service Client!")
        except Exception as e:
            print("Connection to Blob Service Client failed.")
            return str(e)
            

    def blob_upload(self, etl_step):

        pass

    def blob_download(self, etl_step):
        raw_data = json.loads(self.blob_container.download_blob().readall())
        pass

    def get_blob_name(self):
        pass

    def bookmark_blob_name(self, etl_step):
        pass