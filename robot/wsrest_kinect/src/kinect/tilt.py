#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Jul 30, 2011 10:15:15 PM$"

import web
import StringIO
import time
import freenect

urls = (
  "", "reload",
  "/(.*)", "tilt"
)

recurso = { \
    "status" : "ready", \
    "tilt" : "", \
    "led" : "", \
    "accel_x" : "", \
    "accel_y" : "", \
    "accel_z" : "", \
    "id" : 0 \
    }


class reload:
    def GET(self): raise web.seeother('/')
    def POST(self): raise web.seeother('/')

class tilt:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.


    # ============ Final da Inicializacao unica por classe ======

    def freenect_body_get(self, dev, ctx):
        global recurso
#        tilt = freenect.get_tilt_state(dev)
#        print "tilt angle = " + str(tilt.tilt_angle)
#        print "tilt status = " + str(tilt.tilt_status)
#        recurso['tilt'] = str(tilt.tilt_angle)
        acc_xyz = freenect.get_accel(dev)
        recurso['accel_x'] = str(acc_xyz[0])
        recurso['accel_y'] = str(acc_xyz[1])
        recurso['accel_z'] = str(acc_xyz[2])
        raise freenect.Kill

    def freenect_body_post(self, dev, ctx):
        global recurso
        if recurso['tilt'] != "" \
            and int(recurso['tilt']) > -30 and int(recurso['tilt']) <= 30:
            freenect.set_tilt_degs(dev, int(recurso['tilt']))
        led = recurso['led'].lower()
        led_int = 0 if led == 'off' \
            else 1 if led == 'green' \
            else 2 if led == 'red' \
            else 3 if led == 'yellow' \
            else 4 if led == 'blink_yellow' \
            else 5 if led == 'blink_green' \
            else 6 if led == 'blink_red_yellow' \
            else -1
        if led_int >= 0:
            freenect.set_led(dev, 0)
            freenect.set_led(dev, led_int)
        raise freenect.Kill

    def GET(self, name):

        tp = int(time.time() * 1000)
        web.header('Content-Type', 'application/xml')
        global recurso
        freenect.sync_stop()
        freenect.runloop(body=self.freenect_body_get)

        tp = int(time.time() * 1000) - tp
        web.debug('GET total time: ' + str(tp) + " ms")

        return self.to_xml(recurso)


    def POST(self, name):

        tp = int(time.time() * 1000)
        global recurso
        # Atualizando recurso com dados do post.
        self.from_xml(web.data())

        freenect.sync_stop()
        freenect.runloop(body=self.freenect_body_post)

        tp = int(time.time() * 1000) - tp
        web.debug('POST total time: ' + str(tp) + " ms")

        recurso['status'] = 'ready'
        return 'post ok'


    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
#        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  "KinectTiltLed")

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
#                print "key = " + key
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % "KinectTiltLed")
        stream.seek(0)
        return stream.read()

    def from_xml(self, xml):
        #print xml
        # ToDo: Remover tudo que nao estiver dentro da tag do recurso
        global recurso
        recurso['status'] = 'reading xml data'
        for item in recurso.items():
            key, value = item
            inicio = xml.find("<" + key + ">")
            if inicio >= 0:
                final = xml.find("</" + key + ">")
                if inicio >= 0 and final > inicio:
                    # Ignorando atributos 'status' e 'id'.
                    if key != 'status' and key != 'id':
                        stringXml = xml[inicio + len(key) + 2 : final]
                        if len(stringXml) > 0: # Ignorando chaves vazias.
                            # Diferenciando valor (string ou int)
                            if isinstance(recurso[key], str):
                                recurso[key] = stringXml
                            else:
                                recurso[key] = int(stringXml)
        #print recurso


app_tilt = web.application(urls, locals())
