import datetime
import logging
import os
import azure.functions as func

# Reddit Variables
PRAW_ID = os.getenv('praw_id')
PRAW_SECRET = os.getenv('praw_secret')
PRAW_AGENT = os.getenv('praw_agent')

#Azure Variables
AZ_CONNECT = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

def main(mytimer: func.TimerRequest, msg: func.Out[func.QueueMessage]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    msg.set(f"Timer ran atand the secret is {PRAW_SECRET}")
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    logging.info('The secret is %s',PRAW_SECRET)