#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Oct 22, 2011 2:09:19 PM$"


import web
import time

import xml_util
import db_util
import global_data
import http_util


urls = (
        '/(.*)', 'index'
        )

application = web.application(urls, globals())

class index:
    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # Conectando com o BD.
    db=db_util.connect()
    
    # ============ Final da Inicializacao unica por classe ======

    def GET(self, param):
        
        web.header('Content-Type', 'application/xml')
        t0=int(time.time() * 1000)
#        result = xml_util.rdfxml_error("ID not found.")
        result=xml_util.dict_to_rdfxml(\
            {"error" : "ID not found"}\
            , "stm")
        if param:
            try:
                id=int(param)
            except:
                id=0
            
            if id>0:
                # autorizacao.
                server_timeout,client_timeout,client_username\
                    =http_util.http_authorization(global_data.host_auth\
                    ,global_data.access_token\
                    ,http_util.http_get_token_in_header(web))    
                # resposta.
                if server_timeout<=0 or client_timeout<=0:
                    web.ctx.status = '401 Unauthorized'
                    return
        
                result_one=self.get_resource_by_id(id)
                if result_one!=None:
                    result=result_one

        web.debug('GET total time: ' + str(int(time.time()*1000)-t0) + " ms")

        return result


    def POST(self, ignored):
        
        result=xml_util.dict_to_rdfxml(\
            {"rdfs:comment":"Error"}\
            ,"stm")
        # autorizacao.
        server_timeout,client_timeout,client_username\
            =http_util.http_authorization(global_data.host_auth\
            ,global_data.access_token\
            ,http_util.http_get_token_in_header(web))    
        # resposta.
        if server_timeout<=0 or client_timeout<=0:
            web.ctx.status = '401 Unauthorized'
            return
            
        # validando: recurso nao estah vazio.
        resource=web.data()
        if len(resource)>0:
#                # gerando id
#                id=int(time.time()*10000)
            # Gravando no BD.
            result_db=db_util.persist_resource(self.db\
                ,client_username\
                ,resource)
            id=xml_util.key_parent_from_xml\
                (result_db,"id_resource","response")
            result=xml_util.dict_to_rdfxml(\
                {"id_resource":id}\
                , "stm")
        return result

    def get_resource_by_id(self, id):
        # Lendo BD.
        cursor = self.db.cursor()
        cursor.execute('''SELECT resource_text FROM tbl_stm
            WHERE id_resource = %s''', id)
        result = cursor.fetchone()
        if result != None:
            result = result[0]
        # Fechando cursor.
        cursor.close()

        #ToDo:
        # incrementar peso (update weight+1)
        
        return result


if __name__ == "__main__":
    
    global_data.access_token="anonymous"
    global_data.realm="realm@som4r.net"
    global_data.user="stm"
    global_data.passwd="123456"
    global_data.host_auth="localhost:8012"
    
    # authenticate and get token.
    global_data.access_token,xml_resource\
        =http_util.http_authentication(global_data.realm\
        ,global_data.host_auth,global_data.user,global_data.passwd)
#        print "token="+str(global_data.access_token)
    if global_data.access_token is None \
        or (not isinstance(global_data.access_token,str)):
        print "[ERROR] cannot get token."
        
    application.run()