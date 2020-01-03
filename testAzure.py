from azure.storage.blob import BlobServiceClient

service = BlobServiceClient(account_url="https://buildapcscrape.blob.core.windows.net/", credential=credential)
