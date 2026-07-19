from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

#DB SETTINGS
DRIVER = "ODBC+Driver+18+for+SQL+Server"
VAULT_URL = "https://public-health-etl-kv.vault.azure.net"


#Azure Key Vault Secrets
def get_secrets():
    """
    Return dictionary of Azure Vault Secrets
    """
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=VAULT_URL, credential=credential)
    SECRETS = {
        'SERVER' : client.get_secret("db-server").value, 
        'DB' : client.get_secret("db-name").value, 
        'USER' : client.get_secret("db-username").value, 
        'PASS' : client.get_secret("db-password").value,
        'BLOB' : client.get_secret("blob-connection-string").value 
        }
    return SECRETS