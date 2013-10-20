#!/usr/bin/env python

# Copyright (c) 2008 Carnegie Mellon University.
#
# You may modify and redistribute this file under the same terms as
# the CMU Sphinx system.  See
# http://cmusphinx.sourceforge.net/html/LICENSE for more information.


__author__="marcus"
__date__ ="$Nov 14, 2010 3:11:43 PM$"

import web
import subprocess

import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()
import gst

import xml_util
import http_util
import global_data


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

init_gstreamer = True

# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
#, initializer={'logged_in': False})


class index:
    
    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.
    
    #"""Initialize the speech components"""
    #self.init_gst(self)

    pipeline = gst.parse_launch('gconfaudiosrc ! audioconvert ! audioresample '
                                             + '! vader name=vad auto-threshold=true '
                                             + '! pocketsphinx name=asr ! fakesink')
    
    def GET(self, ignored):
#        web.debug('[INFO] get...')
        web.header('Content-Type', 'application/xml')
        global recurso

        # autorizacao.
        server_timeout,client_timeout,client_username\
            =http_util.http_authorization(global_data.host_auth\
            ,global_data.access_token\
            ,http_util.http_get_token_in_header(web))    
        # resposta.
        if server_timeout<=0 or client_timeout<=0:
            web.ctx.status = '401 Unauthorized'
            return
            
        if self.pipeline.get_state()!=gst.STATE_PLAYING:
#            web.debug('[INFO] state_playing...')
            self.pipeline.set_state(gst.STATE_PLAYING)
#        while self.pipeline.get_state() == gst.STATE_PLAYING:
#                 web.debug('[INFO] waiting...')
            #self.tts.say('get.' + recurso['provavel']) 
        
        return xml_util.dict_to_rdfxml(recurso,"listen")

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
        #web.debug('[INFO] asr_result...  text=' + text + " uttid=" + uttid)
        """Forward result signals on the bus to the main thread."""
        global recurso, voice_command
        recurso['result'] = text
        recurso['parcial'] = ""
        recurso['uttid'] = str(uttid)
        
        if len(text)>0 or int(str(uttid))==0:
            # log no servico stm
            recurso_rdfxml=xml_util.dict_to_rdfxml(recurso,"listen")
            xml_response=http_util.http_request('post'\
                ,global_data.host_stm,"/"\
                ,None,global_data.access_token,recurso_rdfxml)
#            id_stm=int(xml_util.key_parent_from_xml\
#                (xml_response,"id_resource","stm"))

            # Respostas automaticas
            # 'nome' do robo.
            if text.lower() in ['robot','bobo']:
                if subprocess.call(["espeak","-vpt","pronto"])!=0: # aqui, o key, r2, sim, r b r
                    web.debug("[ERROR] subprocess.call espeak...")
            # susto
            if text.lower() in ['boo','buhh','poo']:
                if subprocess.call(["espeak","-vpt","susto!"])!=0:
                    web.debug("[ERROR] subprocess.call espeak...")

        struct = gst.Structure('result')
        struct.set_value('hyp', text)
        struct.set_value('uttid', uttid)
        asr.post_message(gst.message_new_application(asr, struct))

    def application_message(self, bus, msg):
        """Receive application messages from the bus."""
        #web.debug('[INFO] application_message...')
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
        web.debug("[INFO] Stopping Listen...")
#        self.pipeline.set_state(gst.STATE_PAUSED)

# ToDo:  Metodo POST? para "silenciar" o pipeline?
#        vader = self.pipeline.get_by_name('vad')
#        vader.set_property('silent', True)


if __name__ == "__main__":
    
    global_data.access_token="anonymous"
    global_data.realm="realm@som4r.net"
    global_data.user="listen"
    global_data.passwd="123456"
    global_data.host_auth="localhost:8012"
    global_data.host_stm="localhost:8098"
    
    # authenticate and get token.
    global_data.access_token,xml_resource\
        =http_util.http_authentication(global_data.realm\
        ,global_data.host_auth,global_data.user,global_data.passwd)
#        print "token="+str(global_data.access_token)
    if global_data.access_token is None \
        or (not isinstance(global_data.access_token,str)):
        print "[ERROR] cannot get token."

    app.run()
