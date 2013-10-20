#!/usr/bin/env python

import web
import time

import global_data
import xml_util
import http_util


urls = (
  "", "reload",
  "/(.*)", "index"
)

class reload:
    def GET(self,none=None): raise web.seeother('/')
    def POST(self,none=None): raise web.seeother('/')

class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # ============ Final da Inicializacao unica por classe ======

    def GET(self, name):

#        print global_data.sleep_thread_ms
        web.header('Content-Type', 'application/xml')

        if len(global_data.resource['inhibited_by']) > 0:
            # Verifica o timeout da inibicao.
            if (int(time.time()*1000)-global_data.resource['inhibited_timestampms']\
                > time_without_movement_ms):
                # Reset.
                global_data.resource['inhibited_by'] = ""
                global_data.resource['inhibited_timestampms'] = 0
                print "reset done"
                # log no servico stm
                recurso_rdfxml=xml_util.dict_to_rdfxml(\
                    {"inhibited_reset_after_ms":time_waiting}\
                    , 'subsumption')
                http_util.http_request('post',url_wsrest_stm,"/"\
                    ,None,None,recurso_rdfxml)

        return xml_util.dict_to_rdfxml(global_data.resource, 'subsumption')

    def POST(self, name):
        t0 = int(time.time() * 1000)

        # reading parameters (supress, inhibit)
        xml = xml_util.key_parent_from_xml(web.data(), 'inhibited_by', 'subsumption')
        if len(xml) > 0:
            global_data.resource['inhibited_by'] = xml
            global_data.resource['inhibited_timestampms'] = int(time.time()*1000)

        web.debug("POST time: " + str(int(time.time() * 1000) - t0) + "ms")

        recurso_rdfxml=xml_util.dict_to_rdfxml(global_data.resource, 'subsumption')
        # log no servico stm
        http_util.http_request('post',global_data.url_wsrest_stm,"/"\
            ,None,None,recurso_rdfxml)

        return recurso_rdfxml


app_index=web.application(urls,locals())
