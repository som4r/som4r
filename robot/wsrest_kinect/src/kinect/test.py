#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Jul 30, 2011 11:40:41 AM$"

import web
import freenect
import time

urls = (
    '/(.*)', 'hello'
)

recurso = { \
    "status" : "ready", \
    "tilt" : "", \
    "led" : "", \
    "id" : 0 \
    }

web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

app = web.application(urls, globals())

class hello:

    def GET(self, name):
        tp = int(time.time() * 1000)
        freenect.runloop(body=self.body)
        if not name:
            name = 'World'

        tp = int(time.time() * 1000) - tp
        web.debug('POST total time: ' + str(tp) + " ms")
        return 'Hello, ' + name + '!'
    
    def body(self, dev, ctx):
        global recurso
        print('led[%d] tilt[%s] accel[%s]' \
            % (-1, freenect.get_tilt_state(dev), freenect.get_accel(dev)))
        freenect.set_tilt_degs(dev, 20)
#        get_tilt_state
#        temp = freenect.get_accel(dev)
#        print ("accel[%s]" % (temp))
#recurso['tilt']
#        web.debug('tilt = ' + recurso['tilt'])
        raise freenect.Kill


if __name__ == "__main__":
    app.run()

