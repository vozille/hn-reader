import datetime

import tornado.ioloop
import tornado.web
from tinydb import TinyDB, where


db = TinyDB('db.json')
posts_db = db.table('posts')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=24)
        posts = posts_db.search(where('timestamp') > int(cutoff_time.strftime("%s")))
        response = ''
        for post in posts:
            category = post.get('category')
            if not category:
                category = 'Uncategorized'
            response = response + "<li><a href=%s>%s</a> - in %s</li>\n" % (post['url'], post['title'], category)
            print post.get('category')
        self.write("""
                        <html>
                            <head></head>
                            <body>
                                <ul>%s</ul>
                            </body>
                        </html>
                   """ % response)

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(5000)
    tornado.ioloop.IOLoop.current().start()
