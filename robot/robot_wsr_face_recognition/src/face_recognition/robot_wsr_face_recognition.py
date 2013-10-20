#!/usr/bin/python

__author__="marcus"
__date__ ="$Aug 20, 2011 12:14:18 PM$"

import web
import StringIO
from string import split
from os.path import basename
import eigenfaces
import time
import os


urls = (
    '/(.*)', 'index'
)

web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

gallery_dir = os.environ['HOME'] + "/robot_/gallery/"
erase_cache_file = True
recurso_nome = "FaceRecognition"
recurso = { \
    "status" : "ready", \
    "local_face" : "", \
    "threshold" : "", \
    "id" : 0 \
    }


class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

#    testimg = ""
#    imgsdir = ""
#    threshold = 3.0
#    egfnum = 6
    # ============ Final da Inicializacao unica por classe ======

    def __init__(self):
        global erase_cache_file
        # Apagando o arquivo na primeira execucao.
        if erase_cache_file == True:
            cachefile=os.path.join(gallery_dir,"saveddata.cache")
            try:
                os.remove(cachefile)
            except:
                erase_cache_file = False
        erase_cache_file = False
        
    def GET(self, name):
        web.header('Content-Type', 'application/xml; charset=utf-8')
        global recurso

        return self.to_xml(recurso)

    def POST(self, name):
        t0 = int(time.time() * 1000)

        global recurso
        # Atualizando recurso com dados do post.
        self.from_xml(web.data())

        # ToDo: Sinalizador. Permite apenas uma transferencia em andamento por vez.
#       # Processamento
        result = self.recognize(recurso.copy())
 
        web.debug("POST time: " + str(int(time.time() * 1000) - t0) + "ms")
        
        self.reset_resource()
        
        return result

    def reset_resource(self):
        global recurso
        recurso['status'] = 'ready'
        recurso['local_face'] = ""
        recurso['threshold'] = ""
        recurso['id'] = 0
            
    def recognize(self, resource):
        # ToDo: Validacao dos parametros.
        
        global gallery_dir
        
        self.testimg = resource['local_face']
        self.imgsdir = gallery_dir
        self.threshold = float(resource['threshold'])
#        self.egfnum = int(resource['engenfaces'])
        parts = split(basename(self.testimg),'.')
        extn = parts[len(parts) - 1]
        web.debug("to match:" + str(self.testimg) + " to all " \
            + str(extn) + " images in directory:" + self.imgsdir)
        self.facet = eigenfaces.FaceRec()
#        self.egfnum = self.set_selected_eigenfaces_count(self.egfnum,extn)
        self.imgnamelist=self.facet.parsefolder(self.imgsdir,extn)
#        web.debug("number of eigenfaces used:" + str(self.egfnum))
#        self.facet.checkCache(self.imgsdir,extn,self.imgnamelist,self.egfnum,self.threshold)
        self.facet.checkCache(self.imgsdir,extn,self.imgnamelist,self.threshold)
#        web.debug("number of eigenfaces used:" + str(self.facet.eigenfaces_calc))
#        mindist,matchfile = self.facet.findmatchingimage(self.testimg,self.egfnum,self.threshold)
        mindist,matchfile = self.facet.findmatchingimage(self.testimg,self.threshold)
        if mindist < 1e-10:
            mindist=0
        if not matchfile:
            result = "<matches></matches><dist></dist>"
        else:
            result = "<matches>"+basename(matchfile)+"</matches><dist>"+str(mindist)+"</dist>"

        web.debug(result)
        return '<result>' + result + '</result>'

#    def set_selected_eigenfaces_count(self,selected_eigenfaces_count,ext):
#        #call eigenfaces.parsefolder() and get imagenamelist
#        self.imgnamelist=self.facet.parsefolder(self.imgsdir,ext)
#        numimgs=len(self.imgnamelist)
#        if(selected_eigenfaces_count >= numimgs  or selected_eigenfaces_count == 0):
#            selected_eigenfaces_count=numimgs/2
#        return selected_eigenfaces_count

    def from_xml(self, xml):
        #print xml
        # ToDo: Remover tudo que nao estiver dentro da tag do recurso
        global recurso
        recurso['status'] = 'reading xml data'
        for item in recurso.items():
            key, value = item
            # Ignorando atributos 'status' e 'id'.
            if key != 'status' and key != 'id':
                inicio = xml.find("<" + key + ">")
                if inicio >= 0:
                    final = xml.find("</" + key + ">")
                    if inicio >= 0 and final > inicio:
                        stringXml = xml[inicio + len(key) + 2 : final]
                        if len(stringXml) > 0: # Ignorando chaves vazias.
                            # Diferenciando valor (string ou int)
                            if isinstance(recurso[key], str):
                                recurso[key] = stringXml
                            else:
                                recurso[key] = int(stringXml)

#                            web.debug("key:value = " + key + " : " + str(recurso[key]))

    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
#        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  recurso_nome)

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % recurso_nome)
        stream.seek(0)
        return stream.read()


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
