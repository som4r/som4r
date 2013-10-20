#!/usr/bin/env python

import web
        
urls = (
  "", "index",
  "/(.*)", "index"
)

app = web.application(urls, globals())

class index:        

    def GET(self,none=None):
        web.header('Content-Type','text/html; charset=utf-8')
        print __file__
        return __file__

if __name__ == "__main__":
    print __file__[2:]
    app.run()