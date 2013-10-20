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

import global_data
import xml_util
import db_util

import subsumption

urls = (
    '/subsumption', subsumption.app_subsumption,
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

global_data.resource = {
    "supressed_by" : "",\
    "supressed_timestampms" : 0\
    }
global_data.subsumption_timeout_ms = 300#6000
global_data.busy = False
global_data.id_supress = 0

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

    # Conectando com o BD.
    db = db_util.connect()

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
        ignore_post = False

        # Suprimido?
        if global_data.id_supress > 0:
            ignore_post = True
            # Verifica o timeout da subsuncao.
            time_waiting = int(time.time()*1000) \
                - int(global_data.resource['supressed_timestampms'])
            if (time_waiting > global_data.subsumption_timeout_ms):
                # Reset.
                global_data.resource['supressed_by'] = ""
                global_data.resource['supressed_timestampms'] = 0
                global_data.resource['supressed_id'] = ""
                global_data.id_supress = 0
                ignore_post = False
                print "reset done after " + str(time_waiting) + "ms"
                # Gravando acao de reset.
                db_util.persist_resource(self.db \
                    , "wsrest_veiculo"\
                    , xml_util.dict_to_rdfxml(\
                    {"supressed_reset_after_ms":time_waiting}\
                    , 'subsumption'))

            # Verifica se origem informou o id_supress correto.
            id_supress_posted=xml_util.key_from_xml(web.data(), 'id_supress')
            if ignore_post and id_supress_posted==str(global_data.id_supress):
                print "accepting post with id_supress: "\
                    + str(global_data.id_supress)
                ignore_post = False
                # Gravando acao de reset.
                db_util.persist_resource(self.db \
                    , "wsrest_veiculo"\
                    , xml_util.dict_to_rdfxml(\
                    {"accepting_post_with_id_supress":global_data.id_supress}\
                    , 'subsumption'))

            if ignore_post:
                print "supressed_by: " + global_data.resource['supressed_by']
                # Gravando acao de bloqueio.
                db_util.persist_resource(self.db \
                    , "wsrest_veiculo"\
                    , xml_util.dict_to_rdfxml(\
                    {'supressed_by':global_data.resource['supressed_by']\
                        ,'supressed_timestampms':global_data.resource\
                        ['supressed_timestampms']\
                        ,'supressed_post_from':"ToDo:from login"\
                        ,'supressed_post_id_supress':global_data.id_supress\
                        ,'id_supress_posted':id_supress_posted\
                    }\
                    , 'subsumption'))

        # Servico nao foi suprimido ou eh um post do supressor?
        if ignore_post == False:
            # Sinalizador. Permite apenas uma transferencia em andamento (dev.write) por vez.
            if global_data.busy == False:
                global_data.busy = True
                # Envia comando ao firmware.
                try:
                    self.to_device()
                except:
                    print "erro ao tentar montar o comando."
                status_returned = recurso['status']
                global_data.busy = False
            else:
                status_returned = 'busy'
                # Gravando status de busy.
                db_util.persist_resource(self.db \
                    , "wsrest_veiculo"\
                    , xml_util.dict_to_rdfxml(\
                    {"supressed_post_because":"busy"}\
                    , 'subsumption'))

            recurso['status'] = 'ready'
            return '<status>' + status_returned + '</status>'
        else:
            return xml_util.dict_to_rdfxml(global_data.resource, 'subsumption')

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

        # Se for girar no eixo a velocidade deve ser minima.
        if recurso['direcao'] in [7,9]:
            recurso['velocidade'] = min(75, recurso['velocidade'])
        # ToDo: Se for mudar o sentido (frente, tras) deve parar antes.

        # Buffer de saida.
        # Array de bytes para enviar ao dispositivo usb.
        buffer_out = numpy.array([0, 0, 0, 0, 0, 0, 0, 0])

        # Montando buffer de saida (para usb). 
        # validando dados do recurso(objeto).
        # ToDo: Validar tambem o id (numero maior q zero)
        if recurso['id_timeout'] == '0' \
            or recurso['direcao'] < 1 or recurso['direcao'] > 9 \
            or recurso['velocidade'] < 0 or recurso['velocidade'] > 100:
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

            # velocidade dos motores sao diferentes de 10% para o robo andar
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
        # disconnect from server
        self.db.close()

if __name__ == "__main__":
    app.run()
