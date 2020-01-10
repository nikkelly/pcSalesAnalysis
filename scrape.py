""" 
Possible considerations:
    Host on Azure Functions to run automatically?
1. Connect to reddit (done)
2. Scrape /r/buildapcsales posts (done)
    a. repeat daily
3. Save all scraped posts to Azure Blob as JSON (done)

#TODO https://docs.microsoft.com/en-us/samples/azure-samples/functions-python-data-cleaning-pipeline/data-cleaning-pipeline/
#TODO https://github.com/wsankey/community
 """
import praw
import datetime
import pandas as pd
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os

from config import PRAW_ID, PRAW_SECRET, PRAW_AGENT, AZ_CONNECT

def reddit_intance():
    # Define Reddit
    reddit = praw.Reddit(client_id=PRAW_ID,client_secret=PRAW_SECRET,user_agent=PRAW_AGENT)
    subreddit = reddit.subreddit('buildapcsales')

    return subreddit

def scrape(subreddit):
    # Set variables
    submissions = []
    today = datetime.datetime.utcnow().strftime('%m-%d-%Y') 
    lastScrape = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    submissionCount = 0
    # Scrape
    for submission in subreddit.new(limit=5):
        # Skip posts that have expired or don't have flair
        if(submission.link_flair_text == None or submission.link_flair_text == 'Expired :table_flip:'):
            continue
        if(datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S') > lastScrape.strftime('%Y-%m-%d %H:%M:%S')):
            submissions.append([submission.title, submission.link_flair_text, submission.id, submission.permalink, submission.url, datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')])
            submissionCount += 1
    submissions = pd.DataFrame(submissions, columns=['title','flair','id','permalink','link','created'])
    print(str(submissionCount) + ' total submissions scraped')

    return submissions, today

def main():
    subreddit = reddit_intance()
    submissions, today = scrape(subreddit)
    upload_results = azure_upload(submissions,today)
    
    
def azure_upload(submissions,today):
    # Setup Azure Environment 
    blob_service_client = BlobServiceClient.from_connection_string(AZ_CONNECT)
    local_path = "./scrapes"
    local_file_name = '{}.json'.format(today)
    upload_file_path = os.path.join(local_path, local_file_name)
    container_name = 'scraped-reddit-data'

    # Export to JSON
    jsonData = submissions.to_json(upload_file_path)
        
    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

    # Upload the created file
    with open(upload_file_path, "rb") as data:
        blob_client.upload_blob(data)

    print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

main()