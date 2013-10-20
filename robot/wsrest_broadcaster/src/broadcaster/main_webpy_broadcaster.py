#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Jan 1, 2011 11:39:03 PM$"


import web

#import numpy
import StringIO
import httplib
import datetime

urls = (
  "/receiver", "receiver",
#  "/provider", "provider",
  "/(.*)", "index"
)


web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

app = web.application(urls, globals())

recursoReceiver = { \
    "id_ws_receiver" : "", \
    "id_tipo_ws" : "", \
    "uri_ws_callback" : ""
    }
recursoReceiverList = [];

# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
    #, initializer={'logged_in': False})




class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):
        web.header('Content-Type', 'application/xml')
        return 'Hello World.'

    def POST(self, name): # Recebe o post do provider e realiza o broadcast.

        t0 = datetime.datetime.now()
        # Verificar se o id do provider esta cadastrado.
        # Persistir? (gravar no banco de dados)?
        # Identificar o id_tipo_ws e listar receivers ?em ordem de prioridade?
        # Extrair do xml o recurso e empacotar numa tag <BroadcasterPostOut>.
        recursoXml = self.get_recurso_xml(web.data(), 'recurso')
#        newPostData = '''"<BroadcasterPostOut>
#            <recurso>''' + recursoXml + '''</recurso>
#            </BroadcasterPostOut>"'''

        # Enviar broadcast ?em threads simultaneas?
        conn = httplib.HTTPConnection("localhost:8090")
        conn.request("POST", "/", recursoXml)
        response = conn.getresponse()
        #print response.status, response.reason
        #200 OK
        #data = response.read()
        conn.close()
        # Atualizar status de retorno de cada receiver que recebeu o post. (?ttl?)

        web.debug('Post Call takes ' + str(datetime.datetime.now()-t0) )
        return '<resposta>' + str(response.status) + '</resposta>'

    def get_recurso_xml(self, xml, resource_name):
        # Retorno padrao - tag recurso, vazio.
        stringXmlResult = "<" + resource_name + "/>"
        # Procurando primeira tag do recurso dentro do parametro xml.
        inicio = xml.find("<" + resource_name + ">")
        if inicio >= 0:
            final = xml.find("</" + resource_name + ">")
            if inicio >= 0 and final > inicio:
                # Retorna apenas o conteudo do recurso.
                stringXmlResult = xml[inicio + len(resource_name) + 2 : final]
        return stringXmlResult

class receiver:

    def POST(self):
        global recursoReceiver, recursoReceiverList
        # Lendo dados recebidos para popular o recursoReceiver.
        self.from_xml(web.data())
        # Armazenando na lista de receivers cadastrados.
        # .copy() garante a transferecia por valor, e nao por referencia.
        recursoReceiverList.append(recursoReceiver.copy())
        return '<status>ok</status>'

    def GET(self):
        global recursoReceiverList
        stream = StringIO.StringIO()
        # Listando receivers cadastrados. (ToDo: listar em formato xml)
        stream.write("Receivers List (%s)\n" % (len(recursoReceiverList)))
        for recurso in recursoReceiverList:
            for item in recurso.items():
                key, value = item
                stream.write('%s = %s\n' % (key, value))
            stream.write("\n") # linha em branco entre os receivers.
        stream.write("\n---")
        stream.seek(0)
        return stream.read()

    def from_xml(self, xml):
        #print xml
        # ToDo: Remover tudo que nao estiver dentro da tag do recurso
        global recursoReceiver
        # Procurando por tags com mesmo nome dos atributos definidos no recurso.
        for item in recursoReceiver.items():
            key, value = item
            inicio = xml.find("<" + key + ">")
            if inicio >= 0:
                final = xml.find("</" + key + ">")
                if inicio >= 0 and final > inicio:
                    stringXml = xml[inicio + len(key) + 2 : final]
                    if len(stringXml) > 0: # Ignorando chaves vazias.
                        # Diferenciando valor (string ou int)
                        if isinstance(recursoReceiver[key], str):
                            recursoReceiver[key] = stringXml
                        else:
                            recursoReceiver[key] = int(stringXml)
        #print recurso


    def __done__(self):
        # Liberando usb
        web.debug('[DONE] Encerrando execucao.')


if __name__ == "__main__":
    app.run()