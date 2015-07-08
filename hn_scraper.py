# -*- coding: utf-8 -*-

import json

import scrapy
from tinydb import TinyDB, where
from tinyrecord import transaction
from readability.readability import Document
from lxml import html

db = TinyDB('db.json')
posts_db = db.table('posts')


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
        with transaction(posts_db) as tr:
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
        with transaction(posts_db) as tr:
            tr.update({'text': text}, where('id')== id)

