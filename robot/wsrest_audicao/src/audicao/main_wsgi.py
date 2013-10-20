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

import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()
import gst


urls = (
        '/(.*)', 'index'
        )

#web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

recurso = { \
    "status" : "ready", \
    "parcial" : "", \
    "resultado" : "", \
    "mensagem" : "", \
    "id" : "", \
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
        web.debug('[INFO] get...')
        web.header('Content-Type', 'application/xml')
        global recurso
 
        if self.pipeline.get_state() != gst.STATE_PLAYING:
            web.debug('[INFO] state_playing...')
            self.pipeline.set_state(gst.STATE_PLAYING)
#        while self.pipeline.get_state() == gst.STATE_PLAYING:
#                 web.debug('[INFO] waiting...')
            #self.tts.say('get.' + recurso['provavel']) 
        
        return self.to_xml(recurso)

#    def listen(self):
#        global recurso
#        self.pipeline.set_state(gst.STATE_PLAYING)

    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  "OuvidoRO")

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % "OuvidoRO")
        stream.seek(0)
        return stream.read()

    def __init__(self):
        web.debug('[INFO] init...')
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
        asr.set_property('lm', './lm/8030.lm')
        asr.set_property('dict', './lm/8030.dic')

        asr.set_property('configured', True)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::application', self.application_message)

        self.pipeline.set_state(gst.STATE_PLAYING)

    def asr_partial_result(self, asr, text, uttid):
        # ToDo: Se houver muitos resultados parciais sem resultado final,
        #   pode usar vader?, silent? e ? to 'restart'.
        web.debug('[INFO] asr_partial_result...  text=' + text + " uttid=" + uttid)
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
        global recurso
        recurso['resultado'] = text
        recurso['parcial'] = ""
        recurso['uttid'] = str(uttid)
        recurso['id'] = str(int(time.time() * 100))
        struct = gst.Structure('result')
        struct.set_value('hyp', text)
        struct.set_value('uttid', uttid)
        asr.post_message(gst.message_new_application(asr, struct))

    def application_message(self, bus, msg):
        """Receive application messages from the bus."""
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
        print "Stoping Ouvido..."
#        self.pipeline.set_state(gst.STATE_PAUSED)

# ToDo:  Metodo POST? para "silenciar" o pipeline?
#        vader = self.pipeline.get_by_name('vad')
#        vader.set_property('silent', True)

application = web.application(urls, globals()).wsgifunc()
