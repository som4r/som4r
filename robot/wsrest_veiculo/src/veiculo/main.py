#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Sep 26, 2010 5:35:11 PM$"

import sys

sys.path.append('/usr/local/lib/python2.6/dist-packages/')

import web
import usb
import numpy
import StringIO
import time

urls = (
        '/(.*)', 'hello'
        )

web.config.debug = False    # Debug true causa problema quando usado junto com sessoes.

app = web.application(urls, globals())

recurso = { \
    "direcao" : 0, \
    "velocidade" : 0, \
    "tempo" : 0, \
    "id_timeout" : "0", \
    "status" : "ready" \
    }

# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
    #, initializer={'logged_in': False})




class hello:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # Inicializando USB
    # find our device
    dev = usb.core.find(idVendor=0x1781, idProduct=0x07d0)
    # was it found?
    if dev is None:
        raise ValueError('[ERRO] Device not found.')
    #else:
    #    tts.say('Device found!')
    #    print 'Device found'

    # Detach kernel driver
    try:
        dev.detach_kernel_driver(0)
    except:
        pass
    # set the active configuration. With no arguments, the first
    # configuration will be the active one
    dev.set_configuration()

    # Claim device
    usb.util.claim_interface(dev, 0)
    #tts.say('success.')
    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):
        web.header('Content-Type', 'application/xml')
        #web.debug(web.ctx.protocol + " " + web.ctx.method + " from " +  web.ctx.ip)
        global recurso
        #recurso["tempo"] += 1
        # ToDo: Nao aceitar chamada com parametro.
#        if not name:
#            name = 'World.'
        return self.to_xml(recurso)

    def POST(self, name):
        #web.debug(web.ctx.protocol + " " + web.ctx.method + " from " +  web.ctx.ip)
        #print name
        global recurso
        # Sinalizador. Permite apenas uma transferencia em andamento (dev.write) por vez.
        if recurso['status'] == 'ready':
            self.to_device()
            status_returned = recurso['status']
        else:
            status_returned = 'busy'

        recurso['status'] = 'ready'
        return '<status>' + status_returned + '</status>'

    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  "VeiculoRO")

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % "VeiculoRO")
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
                    if key != 'status': # Ignorando atributo 'status'.
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

        # Lendo dados recebidos
        recurso['id_timeout'] = '0'
        self.from_xml(web.data())
        recurso['status'] = 'sending to device'

        # Buffer de saida.
        # Array de bytes para enviar ao dispositivo usb.
        buffer_out = numpy.array([0, 0, 0, 0, 0, 0, 0, 0])

        # Montando buffer de saida (para usb).
        # validando dados do recurso(objeto).
        # ToDo: Validar tambem o id (numero maior q zero)
        if recurso['id_timeout'] == '0' \
            or int(recurso['direcao']) < 1 or int(recurso['direcao']) > 9 \
            or int(recurso['velocidade']) < 0 or int(recurso['velocidade']) > 100:
            web.debug('[INFO] Dados incorretos. Nao foram enviados.')
            print recurso
            # Restaurando backup do recurso.
            recurso = recurso_backup
            recurso['status'] = 'post ignored'
            #self.tts.say('Failure!')

        else:
            # byte 0 = 00 (Comando executar)
            # byte 1 = direcao de rotacao dos motores.
            buffer_out[1] = 10 if (recurso['direcao'] >= 1 and recurso['direcao'] <= 3) \
                else 8 if recurso['direcao'] == 4 \
                else 0 if recurso['direcao'] == 5 \
                else 2 if recurso['direcao'] == 6 \
                else 9 if recurso['direcao'] == 7 \
                else 6 if recurso['direcao'] == 9 \
                else 5 if recurso['direcao'] == 8 \
                else 0
                #else 5 if (recurso['direcao'] >= 7 and recurso['direcao'] <= 9) \

            # velocidade dos motores são diferentes de 10% para o robô andar
            #  para frente e levemente para um dos lados.
            # byte 2 = velocidade do motor I (0~100%)
            buffer_out[2] = max(0, (recurso['velocidade'] - 10) \
                if recurso['direcao'] == 3 \
                else recurso['velocidade'])
                #if (recurso['direcao'] == 3 or recurso['direcao'] == 9) \
            # byte 3 = velocidade do motor II (0~100%)
            buffer_out[3] = max(0, (recurso['velocidade'] - 10)) \
                if recurso['direcao'] == 1 \
                else recurso['velocidade']
                #if (recurso['direcao'] == 1 or recurso['direcao'] == 7) \
            # byte 7 (ultimo) informa sequencial do comando.
            buffer_out[7] = 1

            # Enviando e certificando o envio dos dados.
            self.dev.write(1, buffer_out, 0)
            recurso['status'] = 'post ok'
            buffer_in = self.dev.read(129, 8, 0) # 1a. leitura
            if self.compare_arrays(buffer_in, buffer_out) == False:
                buffer_in = self.dev.read(129, 8, 0) # 2a. leitura
                if self.compare_arrays(buffer_in, buffer_out) == False:
                    web.debug('[INFO] Falhou em conferir o envio dos dados.')
                    recurso['status'] = 'post ok without confirmation'

            # Comando executa durante um tempo determinado, depois deve parar o veiculo fobotico.
            if recurso['tempo'] > 0 and recurso['tempo'] <= 2000:
                #web.debug('waiting... ' + str(recurso['tempo']))
                time.sleep(recurso['tempo']/1000.)
                recurso['direcao'] = 5
                recurso['velocidade'] = 0
                recurso['tempo'] = 0
                # Montando buffer do comando parar.
                buffer_out[1] = 0
                buffer_out[2] = 0
                buffer_out[3] = 0
                #buffer_out[7] = 1

                # Enviando e ToDo:certificando o envio dos dados.
                self.dev.write(1, buffer_out, 0)
                recurso['status'] = 'post ok'
                buffer_in = self.dev.read(129, 8, 0) # 1a. leitura


                    #self.tts.say('Failure!')
#                else:
#                    web.debug('Write Ok 2.')
                    #self.tts.say('Success two!')
#            else:
#                web.debug('Write Ok 1.')
                #self.tts.say('Success one!')

    def compare_arrays(self, array1, array2):
        i = 0
        isEqual = True
        while i < 8:
            isEqual = False if array1[i] != array2[i] else isEqual
            i+=1

        return isEqual

    def __done__(self):
        # Liberando usb
        web.debug('[DONE] Encerrando execucao.')
        usb.util.dispose_resources(self.dev)

if __name__ == "__main__":
    app.run()
