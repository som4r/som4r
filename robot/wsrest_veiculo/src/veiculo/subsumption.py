#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Jul 18, 2011 11:40:15 PM$"

import web
import time

import global_data
import xml_util
import db_util

urls = (
  "", "reload",
  "/(.*)", "subsumption"
)

class reload:
    def GET(self): raise web.seeother('/')
    
    def POST(self): raise web.seeother('/')

class subsumption:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # Conectando com o BD.
    db = db_util.connect()

    # ============ Final da Inicializacao unica por classe ======

    def GET(self, name):
        web.header('Content-Type', 'application/xml')
        # Verifica o timeout da subsuncao.
        if global_data.id_supress > 0:
            time_waiting = int(time.time()*1000) \
                - int(global_data.resource['supressed_timestampms'])
            if (time_waiting > global_data.subsumption_timeout_ms):
                # Reset.
                global_data.resource['supressed_by'] = ""
                global_data.resource['supressed_timestampms'] = 0
                global_data.resource['supressed_id'] = ""
                global_data.id_supress = 0
                print "reset done after " + str(time_waiting) + "ms"
                # Gravando acao de reset.
                db_util.persist_resource(self.db \
                    , "wsrest_veiculo"\
                    , xml_util.dict_to_rdfxml(\
                    {"supressed_reset_after_ms":time_waiting}\
                    , 'subsumption'))

        return xml_util.dict_to_rdfxml(global_data.resource, 'subsumption')

    def POST(self, name):
        t0 = int(time.time() * 1000)
        result = ""
        description = xml_util.description_from_rdfxml(web.data(), "subsumption")
        if len(description) > 0:
            # reading parameters (supress, inhibit)
            s_by = xml_util.key_from_xml(description, 'supressed_by')
            if len(s_by) > 0:
                global_data.id_supress = int(time.time() * 10000)
                global_data.resource['supressed_by'] = s_by
                global_data.resource['supressed_timestampms'] = int(time.time()*1000)
                global_data.resource['supressed_id'] = str(global_data.id_supress)
                result = xml_util.dict_to_rdfxml(\
                    {"id_supress": global_data.id_supress}, 'subsumption')
                # Gravando supressao.
                db_util.persist_resource(self.db \
                    , "wsrest_veiculo"\
                    , xml_util.dict_to_rdfxml(global_data.resource\
                    , 'subsumption'))
                
#            xml = xml_util.key_from_xml(description, 'inhibited_by')
#            if len(xml) > 0:
#                global_data.resource['inhibited_by'] = xml
#                global_data.resource['inhibited_timestampms'] = int(time.time()*1000)
#                global_data.id_inhibit = int(time.time() * 10000)
#                result = xml_util.dict_to_rdfxml(\
#                    {"id_inhibit": global_data.id_inhibit}, 'subsumption')
                
        web.debug("POST time: " + str(int(time.time() * 1000) - t0) + "ms")

        return result


app_subsumption = web.application(urls, locals())