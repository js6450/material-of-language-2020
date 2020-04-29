from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
from bezmerizing import Polyline, Path
from flat import document, shape, rgb, rgba, font, strike
from flat.command import moveto, quadto, curveto, lineto, closepath
from numpy.random import uniform, normal, choice
from scipy.stats import truncnorm
from dotenv import load_dotenv
import os
import tweepy
from textblob import TextBlob
import re
from langdetect import detect
import time
from itertools import chain
from copy import copy
from math import sqrt
import opensimplex

def glyphcommands(f, ch):
    try:
        return Path([copy(cmd) for cmd in f.glyph(f.charmap[ord(ch)])])
    except KeyError:
        pass

def advancefor(f, ch):
    return f.advances[f.charmap[ord(ch)]]

def combine_path(f, s):
    text_paths = []
    cx = 0
    for ch in s:
        glyph_path = glyphcommands(f, ch).translate(cx, 0)
        text_paths.append(glyph_path)
        cx += advancefor(f, ch)
    combined = Path(list(chain(*text_paths)))
    return combined

f = font.open("./NotoSans-Regular.ttf")

def generate_path(text, p_sub):
    fsize = 14 + int(10 * p_sub)
    factor = fsize / f.density
    glyph_path = combine_path(f, text).scale(factor)
    pts = []
    for cmd in glyph_path:
        if type(cmd) in (lineto, curveto, quadto):
            pts.append([cx + cmd.x / 2, cy + cmd.y / 2])
        if type(cmd) != type(closepath):
            cx = cmd.x
            cy = cmd.y
    return pts

load_dotenv()

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=False)

app = Flask(__name__)
socketio = SocketIO(app)

tweets = []
lastsent = 0
interval = 3

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        # print("retrieving tweets")
        if len(tweets) > 3:
            tweets.pop(0)
        if hasattr(status, "retweeted_status"):  # Check if Retweet
            try:
                newtweet = status.retweeted_status.extended_tweet["full_text"]
                if detect(newtweet) == 'en':
                    # print(re.sub("http\S+", "", newtweet))
                    tweets.append([re.sub("http\S+", "", newtweet), generate_path(re.sub("http\S+", "", newtweet), TextBlob(newtweet).sentiment[1]), TextBlob(newtweet).sentiment])
            except AttributeError:
                pass
        else:
            try:
                newtweet = status.extended_tweet["full_text"]
                if detect(newtweet) == 'en':
                    # print(re.sub("http\S+", "", newtweet))
                    tweets.append([re.sub("http\S+", "", newtweet), generate_path(re.sub("http\S+", "", newtweet), TextBlob(newtweet).sentiment[1]), TextBlob(newtweet).sentiment])
            except AttributeError:
                pass
        global lastsent
        if int(time.time()) > lastsent + interval:
            socketio.emit('tweet-data', {'data': tweets})
            lastsent = int(time.time())

    def on_error(self, status_code):
        if status_code == 420:
            return False

listener = MyStreamListener()
stream = tweepy.Stream(auth=api.auth, listener=listener)
stream.filter(track=['coronavirus'], is_async=True)

@app.route('/')
def draw():
    return render_template('index.html')

@socketio.on('connect', namespace='/')
def connection():
    emit("connected", {'data': "connected"})

@socketio.on('disconnect', namespace='/')
def disconnection():
    emit("disconnected", {"data": "disconnected"})

@socketio.on("request-data", namespace="/")
def sendData(msg):
    #print("sending tweet data")
    emit('tweet-data', {'data': tweets})

if __name__ == '__main__':
    app.run()