""" Config Vars """
import os 

# Reddit Variables
PRAW_ID = os.getenv('praw_id')
PRAW_SECRET = os.getenv('praw_secret')
PRAW_AGENT = os.getenv('praw_agent')

#Azure Variables
AZ_CONNECT = os.getenv('AZURE_STORAGE_CONNECTION_STRING')