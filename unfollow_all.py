#! /usr/bin/python
import tweepy
from keys import keys

SCREEN_NAME = keys['screen_name']
CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_TOKEN = keys['access_token']
ACCESS_TOKEN_SECRET = keys['access_token_secret']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, 
                 wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

# remove non-followers
friends = api.friends_ids(SCREEN_NAME)

num_unfollow = abs(int(raw_input("Number of friends to unfollow: ")))
inc = 0

for f in friends:
    if inc < num_unfollow:
        try:
            api.destroy_friendship(f)
            print "removing user id %d" % f
            inc += 1
        except:
            print "user id %d not found" % f
    else:
        break
        
