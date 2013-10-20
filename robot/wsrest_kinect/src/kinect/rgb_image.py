#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Ago 21 2011 11:00:00 PM$"

import web
import time
import freenect

from opencv.cv import *
from opencv.highgui import *

#import xml_util
import http_util
import global_data


urls = (
  "", "reload",
  "/(.*)", "rgb_image"
)

class reload:
    def GET(self): raise web.seeother('/')

class rgb_image:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # ============ Final da Inicializacao unica por classe ======

    def GET(self, name):

        tg = int(time.time() * 1000)

        web.header('Content-Type', 'image/png')
        
        # autorizacao.
        server_timeout,client_timeout,client_username\
            =http_util.http_authorization(global_data.host_auth\
            ,global_data.access_token\
            ,http_util.http_get_token_in_header(web))    
        # resposta.
        if server_timeout<=0 or client_timeout<=0:
            web.ctx.status='401 Unauthorized'
            return

        # Lendo imagem rgb do kinect.
        image, timestamp = freenect.sync_get_video()

        full_image_path = "last_rgb.png"
        cvSaveImage(full_image_path, image)

        web.debug('GET total time: ' + str(int(time.time() * 1000) - tg) + " ms")

        # retornando a partir do arquivo gravado.
        return open(full_image_path,"rb").read() # Notice 'rb' for reading images

    def __done__(self):
        # encerrando libfreenect.
        raise freenect.Kill


app_rgb_image = web.application(urls, locals())