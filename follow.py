#! /usr/bin/python
from datetime import datetime
import sqlite3
import tweepy
from keys import keys

# create db
db = sqlite3.connect('data/MyDB.db')
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS follower_db(id INTEGER UNIQUE, create_date TEXT)''')
db.commit()

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

# follow new users
user_screen_name = raw_input('enter user screen name: ')
max_follow = int(raw_input('max follows for this session: '))
followed = 0
date = datetime.strftime(datetime.now(), '%Y-%m-%d')

for user_id in tweepy.Cursor(api.followers_ids, screen_name=user_screen_name).items():
    if followed == max_follow:
	print "All done for today. Kirk Fuller, over and out"
        exit()
    else:
        cursor.execute('''SELECT id FROM follower_db WHERE id = ?''', (user_id,))
	user_id_row = cursor.fetchall()
        if user_id_row is None:
            cursor.execute('''INSERT OR IGNORE INTO follower_db (id, create_date) VALUES (?,?)''', (user_id, date))
	    api.get_user(user_id).follow()
            followed += 1
	    print "followed %d new users" % followed
        else:
            print "user id %d exists in followers_db" % user_id 
