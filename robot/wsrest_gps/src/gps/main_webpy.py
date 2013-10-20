# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Oct 30, 2010 11:59:41 AM$"

import web
import StringIO
import festival
import serial
import time

urls = (
        '/(.*)', 'index'
        )

web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

app = web.application(urls, globals())

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

    # Inicializando TTS
    tts = festival.Festival()
    tts.say('Starting g p s service.')

    # Inicializando GPS
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)


    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):

        web.header('Content-Type', 'application/xml')
        global recurso
        self.read_serial()
        #self.tts.say('Get')
        # ToDo: Nao aceitar chamada com parametro.
#        if not name:
#            name = 'World.'
        return self.to_xml(recurso)

    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
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
        global recurso
        recurso['status'] = 'reading gps data'
        recurso['latitude'] = ''
        recurso['longitude'] = ''
        recurso['altitude'] = ''
        recurso['angulo'] = ''
        recurso['velocidade'] = ''
        recurso['id'] = ''
        for i in range(1, 8):   # 7 mensagens por ciclo
            linha = self.ser.readline()
            lista = linha.split(',')
            if lista[0] == '$GPGGA':
                temp1 = float(lista[2])/100
                temp2 = temp1 if (lista[3] == "N") else (temp1 * (-1))
                recurso['latitude'] = str(temp2)
                temp1 = float(lista[4])/100
                temp2 = temp1 if (lista[5] == "E") else (temp1 * (-1))
                recurso['longitude'] = str(temp2)
                recurso['altitude'] = lista[9]
                recurso['id'] = str(int(time.time() * 100))
                recurso['status'] = 'Ready'
            
            if lista[0] == '$GPRMC':
                recurso['angulo'] = lista[8]
                recurso['velocidade'] = lista[7]


    def __done__(self):
        # Liberando usb
        web.debug('[DONE] wsrest_gps - Encerrando execucao.')
        self.tts.say('Shootting down, g p s.')
        self.ser.close()


if __name__ == "__main__":
    app.run()

