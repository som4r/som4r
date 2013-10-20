#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Jul 18, 2011 11:40:15 PM$"

import web
import StringIO
import time
import freenect
import numpy

urls = (
  "", "reload",
  "/(.*)", "depth"
)

class reload:
    def GET(self): raise web.seeother('/')

class depth:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # ============ Final da Inicializacao unica por classe ======

    def GET(self, name):

        tg = int(time.time() * 1000)

        web.header('Content-Type', 'application/xml')

        stream = StringIO.StringIO()
        stream.write('<%s>' %  "KinectDepth2D")

        # Lendo dados de profundidade.
        depth, timestamp = freenect.sync_get_depth()

        # Menor distancia.
        # No Kinect 2047 indica erro no pixel. Zero tambem?
        discard_h = 32 # de cada lado da largura.
        mins = depth[:,discard_h:-discard_h].min(0)

        for j in range(mins.shape[0]):
            if mins[j] == 0 or mins[j] == 2047:
                # Procurando menor valor nao erro (2047) da coluna j.
                min_value = 2046
                for i in range(depth.shape[0]):
                    # Valor minimo nao nulo, nem erro.
                    if depth[i,j+discard_h] > 0 \
                        and depth[i,j+discard_h] < min_value:
                        min_value = depth[i,j+discard_h]

                mins[j] = min_value

            # gravando xml.
            stream.write('\n<%s>%d</%s>' % ("x" + str(j), mins[j], "x" + str(j)))

        stream.write('\n</%s>' %  "KinectDepth2D")
        stream.seek(0)

        tg = int(time.time() * 1000) - tg
        web.debug('GET total time: ' + str(tg) + " ms")

#        freenect.sync_stop()
        
        return stream.read()

    def __done__(self):
        # encerrando libfreenect.
        raise freenect.Kill


app_depth = web.application(urls, locals())