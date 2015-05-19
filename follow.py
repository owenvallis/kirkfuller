#! /usr/bin/python
import sys
import sqlite3
import tweepy
from datetime import datetime
from keys import keys

SCREEN_NAME = keys["screen_name"]
CONSUMER_KEY = keys["consumer_key"]
CONSUMER_SECRET = keys["consumer_secret"]
ACCESS_TOKEN = keys["access_token"]
ACCESS_TOKEN_SECRET = keys["access_token_secret"]

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth,
                 wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

if (not api):
    print "Can't Authenticate"
    sys.exit(-1)

# grab our datetime objects for tweet created_at compare
d = datetime.now()
last_year = d.replace(year = d.year -1)

# follow new users
screen_name = raw_input("enter user screen name: ")
max_follow = abs(int(raw_input("max follows for this session: ")))
followed = 0

# create db
db = sqlite3.connect("data/MyDB.db")

cursor = db.cursor()
# user ids we already tried to follow
cursor.execute("CREATE TABLE IF NOT EXISTS followed_db(id INTEGER PRIMARY KEY, create_date TEXT)")
# current page for the user for which we are consuming their followers
cursor.execute("CREATE TABLE IF NOT EXISTS follower_page_db(screen_name TEXT PRIMARY KEY, page INTEGER)")
# list of ids for the current page for a specific user
cursor.execute("CREATE TABLE IF NOT EXISTS follower_ids_db(screen_name TEXT, id INTEGER)")
db.commit()

# check to see if we have already started consuming this user's followers
cursor.execute("SELECT * FROM follower_page_db WHERE screen_name=?", (screen_name,))
if cursor.fetchone() is None:
    # if this the first time we've seen this user, then create a new entry
    cursor.execute("INSERT INTO follower_page_db VALUES (?, ?)", (screen_name, 0))
    db.commit

while followed < max_follow:
    # check to see if there are any followers left to consume from last time
    cursor.execute("SELECT id FROM follower_ids_db WHERE screen_name=?", (screen_name,))
    user_id = cursor.fetchone()
    if user_id is None:
        print "fetching the next page of user to follow from %s" % screen_name
        cursor.execute("UPDATE follower_page_db SET page=page+1 WHERE screen_name=?", (screen_name,))
        page = cursor.execute("SELECT page FROM follower_page_db WHERE screen_name=?", (screen_name,))

        ids = api.followers_ids(screen_name=screen_name, page=page)
        for user_id in ids:
            print "adding user %d to the list of pottential followers for %s" % (user_id, screen_name)
            cursor.execute("INSERT INTO follower_ids_db VALUES (?, ?)", (screen_name, user_id))
        db.commit
        continue

    user_id = user_id[0]
    print "removing %d from the list of potential followers for %s" % (user_id, screen_name)
    cursor.execute("DELETE FROM follower_ids_db WHERE id=?", (user_id,))

    cursor.execute("SELECT * FROM followed_db WHERE id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO followed_db VALUES (?, DATE('now'))", (user_id,))
        db.commit
        try:
            tweets = api.user_timeline(user_id=user_id, count=1)
            if len(tweets) > 0:
                if tweets[0].created_at > last_year:
                    api.get_user(user_id).follow()
                    followed += 1
                    print "followed %d. Now following %d new users today" % (user_id, followed)
                else:
                    print "Not following %d. They are a non-active user." % user_id
        except:
            print "user %d has a private timeline" % user_id
    else:
        print "user id %d exists in followers_db" % user_id

print "All done for today. Kirk Fuller, over and out"
db.commit()
db.close()
