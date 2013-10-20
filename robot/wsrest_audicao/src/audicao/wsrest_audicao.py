#!/usr/bin/env python

# Copyright (c) 2008 Carnegie Mellon University.
#
# You may modify and redistribute this file under the same terms as
# the CMU Sphinx system.  See
# http://cmusphinx.sourceforge.net/html/LICENSE for more information.


__author__="marcus"
__date__ ="$Nov 14, 2010 3:11:43 PM$"

import web
import StringIO
import time
import subprocess
import httplib

import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()
import gst

import xml_util


urls = (
        '/(.*)', 'index'
        )

#web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

app = web.application(urls, globals())

recurso = { \
    "parcial" : "", \
    "result" : "", \
    "uttid" : "0"
    }
voice_command = 0 #(0=desativado, 1=ativado)

init_gstreamer = True

# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
#, initializer={'logged_in': False})


class index:
    
    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.
    url_wsrest_voice_command="localhost:8092"
    url_wsrest_stm="localhost:8098"
    
    #"""Initialize the speech components"""
    #self.init_gst(self)

    pipeline = gst.parse_launch('gconfaudiosrc ! audioconvert ! audioresample '
                                             + '! vader name=vad auto-threshold=true '
                                             + '! pocketsphinx name=asr ! fakesink')
    
    def GET(self, ignored):
#        web.debug('[INFO] get...')
        web.header('Content-Type', 'application/xml')
        global recurso

        if self.pipeline.get_state() != gst.STATE_PLAYING:
#            web.debug('[INFO] state_playing...')
            self.pipeline.set_state(gst.STATE_PLAYING)
#        while self.pipeline.get_state() == gst.STATE_PLAYING:
#                 web.debug('[INFO] waiting...')
            #self.tts.say('get.' + recurso['provavel']) 
        
        return xml_util.dict_to_rdfxml(recurso,"audicao")

    def __init__(self):
#        web.debug('[INFO] init...')
        global init_gstreamer
        if init_gstreamer or hasattr(self, 'pipeline') == False:
            init_gstreamer = False
            """Initialize the speech components"""
#            self.pipeline = gst.parse_launch('gconfaudiosrc ! audioconvert ! audioresample '
#                                             + '! vader name=vad auto-threshold=true '
#                                             + '! pocketsphinx name=asr ! fakesink')
            asr = self.pipeline.get_by_name('asr')
            asr.connect('partial_result', self.asr_partial_result)
            asr.connect('result', self.asr_result)
            asr.set_property('lm', './lm/0001.lm')
            asr.set_property('dict', './lm/0001.dic')

            asr.set_property('configured', True)

            bus = self.pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect('message::application', self.application_message)

        self.pipeline.set_state(gst.STATE_PLAYING)

    def asr_partial_result(self, asr, text, uttid):
        # ToDo: Se houver muitos resultados parciais sem resultado final,
        #   pode usar vader?, silent? e ? to 'restart'.
 #       web.debug('[INFO] asr_partial_result...  text=' + text + " uttid=" + uttid)
        """Forward partial result signals on the bus to the main thread."""
        global recurso
        recurso['parcial'] = text + "(" + uttid + ") : "
        struct = gst.Structure('partial_result')
        struct.set_value('hyp', text)
        struct.set_value('uttid', uttid)
        asr.post_message(gst.message_new_application(asr, struct))

    def asr_result(self, asr, text, uttid):
        web.debug('[INFO] asr_result...  text=' + text + " uttid=" + uttid)
        """Forward result signals on the bus to the main thread."""
        global recurso, voice_command
        recurso['result'] = text
        recurso['parcial'] = ""
        recurso['uttid'] = str(uttid)
        
        if int(str(uttid))==1 or len(text)>0:
            # Enviar ao WSR-STM.
            recurso_rdfxml = xml_util.dict_to_rdfxml(recurso, "audicao")
            try:
                conn = httplib.HTTPConnection(self.url_wsrest_stm)
                conn.request("POST", "/", recurso_rdfxml)
                response = conn.getresponse()
            #    xml_response = response.read()
                conn.close()
            except:
                web.debug("Erro ao tentar usar o servico STM.")
            #    xml_response=""
            #id_stm=xml_util.key_from_xml(xml_response,"rdf:id_resource")
            ######

            try:
                # Resposta automatica ao 'nome' do robo.
                if text.lower() in ['robot','bobo']:
                    subprocess.call(["espeak","-vpt","pronto"]) # aqui, o key, r2, sim, r b r

                if text.lower() in ['boo','buhh','poo']:
                    subprocess.call(["espeak","-vpt","susto!"])
            except:
                web.debug("Error: subprocess.call espeak...")

# 20111227 - servico comando de voz deve ser um agente q le
#        if text.lower() in ['voice','command']:
#            message = ""
#            if voice_command == 0:
#                voice_command = 1
#                message = "comando de voz"
#            else:
#                voice_command = 0
#                message = "comando de voz desativado"
#            subprocess.call(["espeak","-vpt", message])
#
#            do wsrest_stm ou do wsrest_audicao.
#        if voice_command == 1 \
#            and len(text) > 0 \
#            and text.lower() not in ['voice command','voice','command']:
#            # Enviando comando para o servico comando de voz
#            recursoXml = "<VoiceCommand><command>" \
#                + text.lower() + "</command><id>" \
#                + recurso['id'] + "</id></VoiceCommand>"
#            web.debug("recurso2voicecommand = " + recursoXml)
#            # Enviar comando.
#            conn = httplib.HTTPConnection(self.url_wsrest_voice_command)
#            conn.request("POST", "/", recursoXml)
#            response = conn.getresponse()
#            conn.close()

        struct = gst.Structure('result')
        struct.set_value('hyp', text)
        struct.set_value('uttid', uttid)
        asr.post_message(gst.message_new_application(asr, struct))

    def application_message(self, bus, msg):
        """Receive application messages from the bus."""
        web.debug('[INFO] application_message...')
        global recurso
        msgtype = msg.structure.get_name()
        if msgtype == 'partial_result':
            self.partial_result(msg.structure['hyp'], msg.structure['uttid'])
        elif msgtype == 'result':
            self.final_result(msg.structure['hyp'], msg.structure['uttid'])
            self.pipeline.set_state(gst.STATE_PAUSED)
            recurso['status'] = 'paused'

#    def partial_result(self, hyp, uttid):
#        web.debug('[INFO] partial_result...')
#        global recurso
#        recurso['possivel'] += hyp + "(" + uttid + ") : "
#
#    def final_result(self, hyp, uttid):
#        web.debug('[INFO] final_result...')
#        global recurso
#        recurso['provavel'] = hyp + "(" + uttid + ")"

    def __done__(self):
        # ToDo:  Logout
        print "Stopping Audicao..."
#        self.pipeline.set_state(gst.STATE_PAUSED)

# ToDo:  Metodo POST? para "silenciar" o pipeline?
#        vader = self.pipeline.get_by_name('vad')
#        vader.set_property('silent', True)


if __name__ == "__main__":
    app.run()
