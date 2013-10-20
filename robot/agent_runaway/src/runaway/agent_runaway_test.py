#!/usr/bin/env python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Oct 2, 2011 2:47:28 PM$"

import web
import time
import thread
import global_data
import xml_util

urls = (
    '/(.*)', 'index'
)
app = web.application(urls, globals())


class index:
    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # ==========

    def GET(self, name):
        return xml_util.dict_to_rdfxml(global_data.resource, 'subsumption')

    def POST(self, name):
        t0 = int(time.time() * 1000)

        xml = xml_util.key_parent_from_xml(web.data(), 'supressed_by', 'subsumption')
        if len(xml) > 0:
            global_data.resource['supressed_by'] = xml
            global_data.resource['supressed_timestamp'] = int(time.time()*1000)
        xml = xml_util.key_parent_from_xml(web.data(), 'inhibited_by', 'subsumption')
        if len(xml) > 0:
            global_data.resource['inhibited_by'] = xml
            global_data.resource['inhibited_timestamp'] = int(time.time()*1000)

        web.debug("POST time: " + str(int(time.time() * 1000) - t0) + "ms")

        return xml_util.dict_to_rdfxml(global_data.resource, 'subsumption')



def run_thread (threadname, sleeptime_ms):
    """This is the thread function to be invoked."""
    cycle_ms = 1000
    subsumption_cycles_timeout = 3
    while True:
        sleep_normal = True
        # Verifica o estado (supressao/inibicao)
        if len(global_data.resource['inhibited_by']) > 0:
            # Verifica o timeout da inibicao.
            if (int(time.time()*1000) \
                - global_data.resource['inhibited_timestamp'] \
                > (subsumption_cycles_timeout * cycle_ms)):
                # Resetando inibicao.
                global_data.resource['inhibited_by'] = ""
                global_data.resource['inhibited_timestamp'] = 0
                print "reset done"
                sleep_normal = False
            else:
                print "inhibited_by: " + global_data.resource['inhibited_by']
        else:
            print "thread loop"

        if sleep_normal:
            time.sleep(cycle_ms/1000)
        
    thread.interrupt_main()



if __name__ == "__main__":

    global_data.resource = {
        "supressed_by" : "", \
        "inhibited_by" : "", \
        "supressed_timestamp" : "", \
        "inhibited_timestamp" : ""
    }

    thread.start_new_thread(run_thread, ("Thread1", 0.1))

    app.run()

#    try:
#        while 1:
#            pass
#    except:
#        print "Exiting...."

