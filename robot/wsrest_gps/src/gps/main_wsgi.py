# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Oct 30, 2010 11:59:41 AM$"

import web
import StringIO
import serial
import time
import subprocess

urls = (
        '/(.*)', 'index'
        )

#web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

recurso = { \
    "status" : "ready", \
    "latitude" : "", \
    "longitude" : "", \
    "altitude" : "", \
    "velocidade" : "", \
    "angulo" : "", \
    "id" : ""
    }

# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
    #, initializer={'logged_in': False})

class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # Permissoes de acesso ao GPS
    subprocess.call(["sudo","chmod","666","/dev/ttyUSB0"])

    # Inicializando GPS
    #ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)


    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):

        web.header('Content-Type', 'application/xml')
        global recurso
        self.read_serial()
        # ToDo: Nao aceitar chamada com parametro.
#        if not name:
#            name = 'World.'
        return self.to_xml(recurso)

    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
        #stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  "GpsRO")

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % "GpsRO")
        stream.seek(0)
        return stream.read()

    def read_serial(self):
	# Inicializando GPS 
	# 20110328 colocada aqui porque dava erro quando colocada na inicializacao (comentado acima).
    	ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        global recurso
        recurso['status'] = 'reading gps data'
        recurso['latitude'] = ''
        recurso['longitude'] = ''
        recurso['altitude'] = ''
        recurso['angulo'] = ''
        recurso['velocidade'] = ''
        recurso['id'] = ''
        for i in range(1, 8):   # 7 mensagens por ciclo
            linha = ser.readline()
            lista = linha.split(',')
            if lista[0] == '$GPGGA':
                recurso['altitude'] = lista[9]
                recurso['id'] = str(int(time.time() * 100))
                recurso['status'] = 'Ready'
            
            if lista[0] == '$GPRMC':
                temp = float(lista[3]) / 100
                graus = int(temp)
                minutos = temp - graus  # somente a parte decimal
                minutos = minutos * 10 / 6    # convertendo para milesimo de minuto
                temp = graus + minutos
                temp = temp if (lista[4] == "N") else (temp * (-1))
                recurso['latitude'] = str(temp)
                temp = float(lista[5]) / 100
                graus = int(temp)
                minutos = temp - graus  # somente a parte decimal
                minutos = minutos * 10 / 6    # convertendo para milesimo de minuto
                temp = graus + minutos
                temp = temp if (lista[6] == "E") else (temp * (-1))
                recurso['longitude'] = str(temp)
                recurso['angulo'] = lista[8]
                recurso['velocidade'] = lista[7]
	
	ser.close()


    def __done__(self):
        # Liberando recursos
        web.debug('[DONE] wsrest_gps - Encerrando execucao.')
        #self.ser.close()


application = web.application(urls, globals()).wsgifunc()

