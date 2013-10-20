#! /usr/bin/python

__author__="marcus"
__date__ ="$Feb 6, 2011 2:49:51 PM$"


import web
import StringIO
import time
import numpy
from pylab import plot, show
#from math import tan
import math
import MySQLdb
import httplib



urls = (
        '/(.*)', 'index'
        )

web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

recurso = { \
    "status" : "ready", \
    "imagem" : "ToDo", \
    "posicao_x" : "", \
    "posicao_y" : "", \
    "posicao_lado" : "", \
    "id" : 0 \
    }

# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
    #, initializer={'logged_in': False})

class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):

        web.header('Content-Type', 'application/xml')
        global recurso
        # ToDo: Nao aceitar chamada com parametro.
#        if not name:
#            name = 'World.'
        return self.to_xml(recurso)

    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
#        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  "FaceDetectRO")

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % "FaceDetectRO")
        stream.seek(0)
        return stream.read()

#    def __done__(self):



application = web.application(urls, globals())

if __name__ == "__main__":
    application.run()

#application = web.application(urls, globals()).wsgifunc()
