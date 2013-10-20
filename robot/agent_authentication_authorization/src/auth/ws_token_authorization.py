#!/usr/bin/env python

__author__="marcus"
__date__ ="$Jan 15, 2012 11:55:00 PM$"

import web
import time

import global_data
import db_util
import xml_util


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

    # Conectando com o BD.
    db = db_util.connect()

    # ============ Final da Inicializacao unica por classe ======

    def GET(self,none=None):
        web.header('Content-Type','text/html; charset=utf-8')
        
#        print "IP="+web.ctx.ip
        # or print web.ctx.environ['REMOTE_ADDR']

        auth=web.ctx.env.get('HTTP_AUTHORIZATION')
#        auth=web.ctx.environ['HTTP_AUTHENTICATE']
        # or = web.ctx.env.get('HTTP_AUTHENTICATE')
#        print auth
        if auth is not None and isinstance(auth,str) and auth[:6]=="token=":
            tokens=auth[6:].split(':')
#            print "TOKENS="+str(tokens)
            if len(tokens)==2:
                timeout_server,timeout_client,client_username\
                    =self.validate_token_authorization(tokens)
#                print "ws_t_autho "+str(timeout_server)\
#                    +" : "+str(timeout_client)+" : "+str(client_username)
                if timeout_server>0 or timeout_client>0:
                    # estah autorizado o acesso.
                    resource={"server_timeout_s":timeout_server\
                        ,"client_timeout_s":timeout_client\
                        ,"client_username":client_username}
                    xml_resource=xml_util.dict_to_rdfxml(resource,'authorization')
#                    # Gravando log da autorizacao
#                    db_util.persist_resource(self.db\
#                        ,"authorization"\
#                        ,xml_util.dict_to_rdfxml(resource,'authorization'))
                    # respondendo.
                    return xml_resource
               
        return

    def POST(self, name):
        web.ctx.status = '401 Unauthorized'
        return
    
    def validate_token_authorization(self,tokens_list):
        
        token_server=tokens_list[0]
        token_client=tokens_list[1]
        timeout_server=0
        timeout_client=0
        username=""
        
        # validar token no BD
        cursor=self.db.cursor()
        sql="""select id_resource,resource_text from tbl_stm 
                where id_source='authentication'
                 and resource_text like '"""
        sql_token=sql+"%<token>"+token_server+"</token>%'"
#        print sql_token
#        try:
        # validando token do servico/agente servidor.
        if cursor.execute(sql_token):
            result_set=cursor.fetchone()
#            print result_set[0]
            # calculando timeout do token.
            timeout_server=global_data.token_timeout_s\
                -int((int(time.time()*10000)-int(result_set[0]))/10000)
#            print "timeout="+str(global_data.token_timeout_s)
#            print int(time.time()*10000)
#            print result_set[0]
            timeout_server=0 if timeout_server<0 else timeout_server
#            print timeout_server

            # validando o token do servico/agente cliente.
            sql_token=sql+"%<token>"+token_client+"</token>%'"
#            print sql_token
            if cursor.execute(sql_token):
                result_set=cursor.fetchone()
                # calculando timeout do token.
                timeout_client=global_data.token_timeout_s\
                    -int((int(time.time()*10000)-int(result_set[0]))/1000)
                timeout_client=0 if timeout_client<0 else timeout_client  
                username=xml_util.key_parent_from_xml\
                (result_set[1],"username","authentication")
#                print result_set[1]
#                print "username === "+username
#        finally:
#            # retorna o timeout do token.
#            print "[Error] TODO: show error message"

        return timeout_server,timeout_client,username

app_authorization=web.application(urls,locals())


