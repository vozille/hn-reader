# -*- coding: utf-8 -*-

import time
import json

import scrapy
from tinydb import TinyDB, where
from tinyrecord import transaction
from readability.readability import Document
from lxml import html
from sklearn.externals import joblib


db = TinyDB('db.json')
posts_db = db.table('posts')
clf = joblib.load('clf.pkl')
count_vect = joblib.load('count_vect.pkl')
tfidf_transformer = joblib.load('tfidf_transformer.pkl')


class HNSpider(scrapy.Spider):
    name = 'hackernews'
    start_urls = ['https://hacker-news.firebaseio.com/v0/topstories.json']

    def parse(self, response):
        post_ids = json.loads(response.body_as_unicode())
        for id in post_ids:
            post_url = 'https://hacker-news.firebaseio.com/v0/item/%s.json' % str(id)
            yield scrapy.Request(post_url, callback=self.parse_post)

    def parse_post(self, response):
        response_json = json.loads(response.body_as_unicode())
        if response_json.get('text'):
            cleaned_html = Document(response.body).summary()
            text = html.fromstring(cleaned_html).text_content()
            response_json['text'] = text
            X_counts = count_vect.transform([text])
            X_tfidf = tfidf_transformer.transform(X_counts)
            predicted = clf.predict(X_tfidf)[0]
            print(predicted, response.url)
            response_json['category'] = predicted
        with transaction(posts_db) as tr:
            response_json['timestamp'] = int(time.time())
            tr.insert(response_json)
        if response_json['url']:
            request = scrapy.Request(response_json['url'],
                                     callback=self.parse_link_content)
            request.meta['id'] = response_json['id']
            yield request

    def parse_link_content(self, response):
        id = response.meta['id']
        cleaned_html = Document(response.body).summary()
        text = html.fromstring(cleaned_html).text_content()
        X_counts = count_vect.transform([text])
        X_tfidf = tfidf_transformer.transform(X_counts)
        predicted = clf.predict(X_tfidf)[0]
        print(predicted, response.url)
        with transaction(posts_db) as tr:
            tr.update({'text': text, 'category': predicted}, where('id') == id)
