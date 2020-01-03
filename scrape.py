""" 
1. Connect to reddit
2. Scrape /r/buildapcsales posts
    a. repeat daily
3. Save all scraped posts to Azure Blob as JSON
    a. https://pypi.org/project/azure-storage-blob/
 """
import praw
import config
import datetime
import pandas as pd

reddit = praw.Reddit(client_id=config.CLIENT_ID,client_secret=config.CLIENT_SECRET,user_agent=config.USER_AGENT,username=config.USERNAME,password=config.PASSWORD)
subreddit = reddit.subreddit('buildapcsales')

submissions = []

lastScrape = datetime.datetime.utcnow() - datetime.timedelta(hours=24)

for submission in subreddit.new(limit=3):
    submissions.append([submission.title, submission.id, submission.permalink, submission.url, datetime.datetime.fromtimestamp(submission.created_utc)])

submissions = pd.DataFrame(submissions, columns=['title','id','permalink','link','created'])
jsonData = submissions.to_json()
print(jsonData)