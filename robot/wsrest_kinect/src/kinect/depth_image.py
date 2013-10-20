#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Ago 6, 2011 12:20:15 PM$"

import web
import time
import freenect
import numpy

import frame_convert
#import Image
import cv

from opencv.cv import *
from opencv.highgui import *

urls = (
  "", "reload",
  "/(.*)", "depth_image"
)

class reload:
    def GET(self): raise web.seeother('/')

class depth_image:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # ============ Final da Inicializacao unica por classe ======

    def GET(self, name):

        tg = int(time.time() * 1000)

        web.header('Content-Type', 'image/png')

        # Lendo dados de profundidade.
        depth, timestamp = freenect.sync_get_depth()

        # Tentando converter para imagem gravavel.
        numpy.clip(depth, 0, 2 ** 10 - 1, depth)
        depth >>= 2
        depth = depth.astype(numpy.uint8)
        image = cvCreateImage((depth.shape[1], depth.shape[0]),
             IPL_DEPTH_8U, 1)
        cvCopy( depth, image )
        full_image_path = "last_depth.png"
        cvSaveImage(full_image_path, image)

        web.debug('GET total time: ' + str(int(time.time() * 1000) - tg) + " ms")

        # retornando a partir do arquivo gravado.
        return open(full_image_path,"rb").read() # Notice 'rb' for reading images

    def __done__(self):
        # encerrando libfreenect.
        raise freenect.Kill


app_depth_image = web.application(urls, locals())