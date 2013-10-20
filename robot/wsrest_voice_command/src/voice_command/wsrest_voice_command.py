#! /usr/bin/python

__author__="marcus"
__date__ ="$Jun 24, 2011 11:22:50 AM$"


import web
import StringIO
import time
import httplib

urls = (
        '/(.*)', 'index'
        )

web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.


recurso = { \
    "status" : "ready", \
    "command" : "", \
    "id" : 0 \
    }


class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.
    url_wsrest_veiculo = "localhost:8080"

    def GET(self, name):

        web.header('Content-Type', 'application/xml')
        global recurso

        tg = int(time.time() * 1000)

        # ToDo: Nao aceitar chamada get com parametro.
#        if not name:
#            name = 'World.'
        tg = int(time.time() * 1000) - tg
        web.debug('GET total time: ' + str(tg) + " ms")

        return self.to_xml(recurso)
    
    def POST(self, name):

        global recurso
        # Sinalizador. Permite apenas uma transferencia em andamento por vez.
        if recurso['status'] == 'ready':
            self.execute_command()
            status_returned = recurso['status']
        else:
            status_returned = 'busy'

        recurso['status'] = 'ready'
        return '<status>' + status_returned + '</status>'
    
    def execute_command(self):
        global recurso
        # Lendo dados recebidos
        self.from_xml(web.data())
        #web.debug("recurso IN = " + web.data())
        recurso['status'] = 'sending to device'
        command = recurso['command'].upper()

        # ignorando comandos nao cadastrados
        ignore_command = True

        direcao = "5"
        velocidade = "0"
        # Direcao e/ou velocidade
        if command == "STOP":
            direcao = "5"
            ignore_command = False
        elif command == "AHEAD":
            direcao = "2"
            ignore_command = False
        elif command == "BACK":
            direcao = "8"
            ignore_command = False
        elif command == "RIGHT":
            direcao = "6"
            ignore_command = False
        elif command == "LEFT":
            direcao = "4"
            ignore_command = False
        elif command == "AHEAD RIGHT":
            direcao = "3"
            ignore_command = False
        elif command == "AHEAD LEFT":
            direcao = "1"
            ignore_command = False
        elif command in ["FASTER","SLOWER"]:
            ignore_command = False
            # Lendo a velocidade atual.
            conn = httplib.HTTPConnection(self.url_wsrest_veiculo)
            conn.request("GET", "/")
            response = conn.getresponse()
            xml_veiculo = response.read()
            conn.close()
            direcao = self.key_from_xml(xml_veiculo, "direcao")
            velocidade = self.key_from_xml(xml_veiculo, "velocidade")
#            web.debug("velocidade antes = " + velocidade)
            if command == "FASTER":
                velocidade = str(min(int(velocidade) + 10, 100))
            else:
                velocidade = str(max(int(velocidade) - 10, 70))
#            web.debug("velocidade depois = " + velocidade)

        # Ignorando o comando.
        if not ignore_command:
            # Velocidade
            # Se parar entao velocidade zero.
            if (int(direcao) == 5 or int(direcao) == 0):
                velocidade = "0"
            # Senao se velocidade zero entao velocidade baixa.
            elif int(velocidade) == 0:
                velocidade = "80"

    #        web.debug("velocidade final = " + velocidade)

            # Montando recurso
            recursoXml = "<VeiculoRO>" \
                + "<direcao>" + direcao + "</direcao>" \
                + "<velocidade>" + velocidade + "</velocidade>" \
                + "<id_timeout>" + str(int(time.time() * 100)) + "</id_timeout>" \
                + "</VeiculoRO>"
            #web.debug("recurso OUT = " + recursoXml)
            # Enviar comando.
            conn = httplib.HTTPConnection(self.url_wsrest_veiculo)
            conn.request("POST", "/", recursoXml)
            response = conn.getresponse()
            conn.close()
            recurso['status'] = "post ok"
            
        else:
            recurso['status'] = "post ok, command ignored"

        return

    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
#        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  "VoiceCommand")

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % "VoiceCommand")
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
                    if key != 'status' and key != 'id': # Ignorando atributo 'status'.
                        stringXml = xml[inicio + len(key) + 2 : final]
                        if len(stringXml) > 0: # Ignorando chaves vazias.
                            # Diferenciando valor (string ou int)
                            if isinstance(recurso[key], str):
                                recurso[key] = stringXml
                            else:
                                recurso[key] = int(stringXml)

    def key_from_xml(self, xml, key):
        result = ""
        inicio = xml.find("<" + key + ">")
        if inicio >= 0:
            final = xml.find("</" + key + ">")
            if inicio >= 0 and final > inicio:
                result = xml[inicio + len(key) + 2 : final]
        return result

#application = web.application(urls, globals()).wsgifunc()

application = web.application(urls, globals())

if __name__ == "__main__":
    application.run()
