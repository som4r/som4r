#!/usr/bin/env python

import time
import thread
import web

import global_data
import ws_digest_authentication
import ws_token_authorization
import db_util


urls = (
    "/authentication",ws_digest_authentication.app_authentication,
    "/authorization",ws_token_authorization.app_authorization,
    "/(.*)", "getout"
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
    
    init=True
    while True:
        
        #TODO: Executar processos do agente.
        
        # remover tokens ao iniciar
        if init==True:
            init=False
            cursor=db.cursor()
            # Prepare SQL query to DELETE tokens.
            sql="delete from tbl_stm where id_source='authentication'"
            try:
               # Execute the SQL command
               cursor.execute(sql)
               # Commit your changes in the database
               db.commit()
            except:
               # Rollback in case there is any error
               db.rollback()
       
    
        # dormir.
        time.sleep(global_data.sleep_thread_ms/1000.)

    thread.interrupt_main()


if __name__=="__main__":
    # Conectando com o BD.
    db=db_util.connect()


    global_data.url_wsrest_stm="localhost:8098"
    global_data.sleep_thread_ms=60000
    global_data.realm="realm@som4r.net"
    global_data.opaque="5ccc069c403ebaf9f01fdcd98b7102dd"
    global_data.valid_nonce={}
    # TODO: configuracoes
    # usar metodo de seguranca http digest
    global_data.conf_http_digest=True
    # so emitir tokens para servicos/agentes locais.
    global_data.conf_only_localhost=True#False
    # timeout do token.
    global_data.token_timeout_s=3600*24#300


    thread.start_new_thread(run_thread\
        ,("Thread1",global_data.sleep_thread_ms))

    app.run()

#    try:
#        while 1:
#            pass
#    except:
#        print "Exiting...."

