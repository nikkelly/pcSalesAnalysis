import datetime
import logging
import praw
import azure.functions as func
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import random
import json

#TODO: Remove pandas dependance for JSON
#TODO: Might be able to upload file to container with the same Body/Object items as AWS S3 (wsankey)

def main(mytimer: func.TimerRequest, outToBlob: func.Out[func.InputStream]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    
    subreddit = reddit_instance()
    submissions, today = scrape(subreddit)

    if mytimer.past_due:
        logging.info('The timer is past due!')
    # Add logging 
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

    submissions = json.dumps(submissions)
    
    return submissions, today
    