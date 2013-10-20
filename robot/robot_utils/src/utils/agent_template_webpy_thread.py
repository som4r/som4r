#!/usr/bin/env python

import time
import thread
import httplib
import web

import global_data
import agent_template_webpy_index


urls = (
    "/teste",agent_template_webpy_index.app_index,
    "/(.*)", "getout"
#    "/",agent_template_webpy_index.app_index,
#    "/(.*)", "redir"
)

class getout:
    def GET(self,none=None):
        web.ctx.status = '401 Unauthorized'
        return
    
    def POST(self,none=None):
        web.ctx.status = '401 Unauthorized'
        return

app = web.application(urls, globals())


def run_thread (threadname, sleeptime_ms):
    """This is the thread function to be invoked."""
#    global url_wsrest_stm

    while True:
        # Verifica o estado da inibicao.
        # Agente foi inibido?
        if len(global_data.resource['inhibited_by']) > 0:
            # Verifica o timeout da inibicao.
            if (int(time.time()*1000)-global_data.resource['inhibited_timestampms']\
                > time_without_movement_ms):
                # Reset.
                global_data.resource['inhibited_by'] = ""
                global_data.resource['inhibited_timestampms'] = 0
                print "reset done"
                #TODO: log no servico stm
            else:
                print "inhibited_by: " + global_data.resource['inhibited_by']
                #TODO: log no servico stm

        # Agente nao foi inibido.
        # Executar processo do agente.
        if len(global_data.resource['inhibited_by']) == 0:

            t0 = int(time.time() * 1000)
            t_ = int(time.time() * 1000)

        print "here..."

        # dormir.
        time.sleep(global_data.sleep_thread_ms/1000.)

    thread.interrupt_main()


if __name__=="__main__":

    global_data.resource={
        "inhibited_by":"", \
        "inhibited_timestamp":""
    }
    
    global_data.url_wsrest_stm="localhost:8098"
    global_data.sleep_thread_ms=2000

    thread.start_new_thread(run_thread\
        ,("Thread1",global_data.sleep_thread_ms))

    app.run()

#    try:
#        while 1:
#            pass
#    except:
#        print "Exiting...."

