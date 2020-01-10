import datetime
import logging
import praw
import pandas as pd
import azure.functions as func
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import random

#TODO: Remove pandas dependance for JSON

def main(mytimer: func.TimerRequest, outToBlob: func.Out[func.InputStream]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    
    subreddit = reddit_instance()
    submissions, today = scrape(subreddit)
    # upload_results = azure_upload(submissions,today)
    jsonData = azure_upload(submissions,today)

    if mytimer.past_due:
        logging.info('The timer is past due!')
    # Add logging 
    logging.info('Python processed %s', jsonData)
    logging.info('jsonData = %s', jsonData)
    logging.info('submissions = %s', submissions)

    # Save JSON to blob
    outToBlob.set(submissions)

def reddit_instance():
    # Define Reddit
    reddit = praw.Reddit(client_id=os.environ['PRAW_ID'],client_secret=os.environ['PRAW_SECRET'],user_agent=os.environ['PRAW_AGENT'])
    subreddit = reddit.subreddit('buildapcsales')

    return subreddit

def scrape(subreddit):
    # Set variables
    submissions = []
    today = datetime.datetime.utcnow().strftime('%m-%d-%Y') 
    lastScrape = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    submissionCount = 0
    # Scrape
    for submission in subreddit.new(limit=None):
        # Skip posts that have expired or don't have flair
        if(submission.link_flair_text == None or submission.link_flair_text == 'Expired :table_flip:'):
            continue
        if(datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S') > lastScrape.strftime('%Y-%m-%d %H:%M:%S')):
            submissions.append([submission.title, submission.link_flair_text, submission.id, submission.permalink, submission.url, datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')])
            submissionCount += 1
    submissions = pd.DataFrame(submissions, columns=['title','flair','id','permalink','link','created'])
    logging.info(str(submissionCount) + ' total submissions scraped')

    return submissions, today
    
def azure_upload(submissions,today):
    # Setup Azure Environment 
    blob_service_client = BlobServiceClient.from_connection_string(os.environ['AZURE_STORAGE_CONNECTION_STRING'])
    local_path = "./scrapes"
    local_file_name = '{}+{}.json'.format(today,random.randint(1,10000))
    container_name = 'scraped-reddit-data'

    # Export to JSON
    jsonData = submissions.to_json(local_file_name)
        
    # # Create a blob client using the local file name as the name for the blob
    # blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

    # # Upload the created file
    # with open(local_file_name, "rb") as data:
    #     blob_client.upload_blob(data)

    # logging.info("\nUploading to Azure Storage as blob:\n\t" + local_file_name)
    return jsonData