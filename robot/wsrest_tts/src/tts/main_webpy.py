#! /usr/bin/python

__author__="marcus"
__date__ ="$Oct 23, 2010 10:42:11 PM$"


import web
import StringIO
import festival
import time

urls = (
        '/(.*)', 'hello'
        )

web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

app = web.application(urls, globals())

recurso = { \
    "status" : "ready", \
    "texto" : "", \
    "id" : 0 \
    }

# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
    #, initializer={'logged_in': False})

class hello:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # Inicializando TTS
    tts = festival.Festival()
    #tts.say('Starting t t s.')

    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):

        web.header('Content-Type', 'application/xml')
        global recurso
        #self.tts.say('Get')
        # ToDo: Nao aceitar chamada com parametro.
#        if not name:
#            name = 'World.'
        return self.to_xml(recurso)

    def POST(self, name):

        global recurso
        # Sinalizador. Permite apenas uma transferencia em andamento (dev.write) por vez.
        if recurso['status'] == 'ready':
            self.to_device()
            #self.tts.say('Post')
            status_returned = recurso['status']
        else:
            status_returned = 'busy'

        recurso['status'] = 'ready'
        #recurso['texto'] = ''
        return '<status>' + status_returned + '</status>'

    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  "TtsRO")

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % "TtsRO")
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
        #print recurso

    def to_device(self):
        global recurso

        # Backup do recurso
        recurso_backup = recurso.copy()

        # Lendo dados recebidos (exceto status e id)
        self.from_xml(web.data())
        recurso['status'] = 'sending to device'

        # ToDo: validar dados do recurso(objeto).
        # ToDo: Validar texto com palavras bloqueadas.
        texto = recurso['texto']
        if not isinstance(texto, str) or len(texto) == 0:
            web.debug('[INFO] Dados incorretos. Nao foram enviados ao dispositivo.')
            print recurso
            # Restaurando backup do recurso.
            recurso = recurso_backup
            recurso['status'] = 'post ignored'
            #self.tts.say('Failure!')

        else:
            self.tts.say(texto)
            recurso['status'] = 'post ok'
            # Identificador timestamp
            recurso['id'] = str(int(time.time() * 100))
            

    def __done__(self):
        # Encerrando
        web.debug('[DONE] wsrest_tts - Encerrando execucao.')
        self.tts.say('Shootting down, t t s.')


if __name__ == "__main__":
    app.run()
