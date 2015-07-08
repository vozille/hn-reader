# -*- coding: utf-8 -*-

import time

import praw
from tinydb import TinyDB
from tinyrecord import transaction
from readability.readability import Document
from lxml import html
import grequests

db = TinyDB('reddit.json')
reddit_db = db.table('reddit')

REDDIT_CATEGORIES = [
    ('programming', 'machinelearning', 50),
    ('programming', 'datascience', 50),
    ('programming', 'programming', 50),
    ('programming', 'linux', 50),
    ('programming', 'python', 25),
    ('programming', 'rust', 25),
    
    ('entrepreneurship', 'entrepreneur', 75),
    ('entrepreneurship', 'startups', 75),
    ('entrepreneurship', 'business', 75),
    ('entrepreneurship', 'finance', 75),

    ('design', 'web_design', 150),
    ('design', 'graphic_design', 150),

    ('entertainment', 'music', 75),
    ('entertainment', 'movies', 75),
    ('entertainment', 'books', 75),
    ('entertainment', 'television', 75),

    ('science', 'science', 50),
    ('science', 'physics', 50),
    ('science', 'chemistry', 50),
    ('science', 'biology', 50),
    ('science', 'math', 50),
    ('science', 'space', 50),

    ('security', 'security', 100),
    ('security', 'crypto', 100),
    ('security', 'privacy', 100),

    ('worldnews', 'worldnews', 100),
    ('worldnews', 'news', 100),

    ('technews', 'technology', 100),
    ('technews', 'futurology', 100),
]

reddit = praw.Reddit(user_agent='Scraping top posts for HN classifier')


def get_top_subreddit_posts(category, limit=100):
    return reddit.get_subreddit(category).get_top_from_week(limit=limit)


def get_link_content(url):
    try:
        print "Processing url: %s" % url
        response = grequests.map([grequests.get(url)])[0]
        if response.status_code == 403 or \
                        response.status_code == 404:
            return None
        cleaned_html = Document(response.content).summary()
        text = html.fromstring(cleaned_html).text_content()
    except Exception as e:
        print e
        text = None
    return text


def get_subreddit_samples(category, subreddit, posts):
    for post in posts:
        print(subreddit + ': ' + post.url)
        if post.is_self:
            content = post.selftext
        else:
            content = get_link_content(post.url)
        if content:
            with transaction(reddit_db) as tr:
                tr.insert({
                    'url': post.url,
                    'text': content,
                    'label': category,
                })


def get_reddit_samples():
    # threads = []
    for category, subreddit, limit in REDDIT_CATEGORIES:
        subbreddit_top_posts = list(get_top_subreddit_posts(subreddit, limit))
        get_subreddit_samples(category, subreddit, subbreddit_top_posts)
        time.sleep(3) # No more than 30 requests per minute

if __name__ == '__main__':
    get_reddit_samples()
