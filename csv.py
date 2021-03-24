import tweepy
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from time import strftime, gmtime

def execute():

    # Authenticate to Twitter
    authenticate_path = Path("authenticate.json")

    if authenticate_path.exists():
        with open(authenticate_path) as f:
            authenticate = json.load(f)
        first = authenticate["consumer_key"]
        second = authenticate["consumer_secret"]
    else:
        first = input("consumer_key: ")
        second = input("consumer_secret: ")
        with open("authenticate.json","w") as f:
            json.dump({"consumer_key":first,"consumer_secret":second},f)

    auth = tweepy.OAuthHandler(first,second)

    access_token_path = Path("access_token.json")
    if access_token_path.exists():
        with open(access_token_path) as f:
            access_token = json.load(f)
        auth.set_access_token(access_token["token"],access_token["secret"])
    else:
        try:
            redirect_url = auth.get_authorization_url()
        except tweepy.TweepError:
            print('Error! Failed to get request token.')

        print(redirect_url)
        verifier = input("verification code: ")

        try:
            auth.get_access_token(verifier)
        except tweepy.TweepError:
            print('Error! Failed to get access token.')

        with open("access_token.json","w") as f:
            json.dump({"token":auth.access_token,"secret": auth.access_token_secret},f)

    # Create API object
    api = tweepy.API(auth)

    progress_path = Path("progress.json")
    if progress_path.exists():
        with open(progress_path) as f:
            file = json.load(f)
        last_line = file["last_line"]
    else:
        with open("progress.json","w") as f:
            json.dump({"last_line":0},0)

    tweets = get_tweets("example.csv")
    for tweet in tweets:
        # calcula quanto falta pra postagem
        date = tweet["DiaPost"] + tweet["HoraPost"]
        date_formt = datetime.strptime(date,"%d/%m/%Y%H:%M")
        # print(date_formt)
        #current date and time
        wait_time = date_formt - datetime.now()
        if wait_time.total_seconds() > 0:
            time.sleep(wait_time.total_seconds())

        # Texto
        api.update_status(tweet["Tweet1"])
        last_tweet = api.user_timeline(id = api, count = 1)[0]
        # Imagens
        api.update_with_media(tweet["Tweet2"],in_reply_to_status_id=last_tweet.id)
        last_tweet = api.user_timeline(id = api, count = 1)[0]
        # Links
        api.update_status(tweet["Tweet3"],in_reply_to_status_id=last_tweet.id)

        # Atualiza postagens
        # last_line = last_line + 1
        # with open("progress.json","w") as f:
            # json.dump({"last_line":last_line},f)

    # auth.set_access_token("ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")

def get_tweets(csva):
    tweets = []
    reader = csv.DictReader(open(csva))
    return reader

if __name__ == '__main__':
    # get_tweets("example.csv")
    execute()