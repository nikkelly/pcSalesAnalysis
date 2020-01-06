""" 
Possible considerations:
    Host on Azure Functions to run automatically
1. Connect to reddit (done)
2. Scrape /r/buildapcsales posts (done)
    a. repeat daily
3. Save all scraped posts to Azure Blob as JSON
 """
import praw
import config
import datetime
import pandas as pd

reddit = praw.Reddit(client_id=config.CLIENT_ID,client_secret=config.CLIENT_SECRET,user_agent=config.USER_AGENT,username=config.USERNAME,password=config.PASSWORD)
subreddit = reddit.subreddit('buildapcsales')

submissions = []

lastScrape = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
submissionCount = 0
for submission in subreddit.new(limit=None):
    # Skip posts that have expired or don't have flair
    if(submission.link_flair_text == None or submission.link_flair_text == 'Expired :table_flip:'):
        continue
    if(datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S') > lastScrape.strftime('%Y-%m-%d %H:%M:%S')):
        submissions.append([submission.title, submission.link_flair_text, submission.id, submission.permalink, submission.url, datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')])
        submissionCount += 1

print(str(submissionCount) + ' total submissions scraped')

submissions = pd.DataFrame(submissions, columns=['title','flair','id','permalink','link','created'])
todaysDate = datetime.date.today()
jsonData = submissions.to_json(r'testFile.json')