#! /usr/bin/python

__author__="marcus"
__date__ ="$Oct 23, 2010 10:42:11 PM$"


import web
#from espeak import espeak
import subprocess

import xml_util
import http_util
import global_data


urls = (
        '/(.*)', 'index'
        )

#web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

app = web.application(urls, globals())


class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):
        
        web.header('Content-Type', 'application/xml')        

        # get client token in header.
#        client_token=http_util.http_get_token_in_header(web)
        # autorizacao.
        server_timeout,client_timeout,client_username\
            =http_util.http_authorization(global_data.host_auth\
            ,global_data.access_token\
            ,http_util.http_get_token_in_header(web))    
        # resposta.
        if server_timeout<=0 or client_timeout<=0:
            web.ctx.status = '401 Unauthorized'
            return

        xml_response=xml_util.dict_to_rdfxml(\
            {"text_to_speech":global_data.resource['text_to_speech'],\
            "id":global_data.tts_id}\
            ,'tts')
        
        return xml_response

    def POST(self, name):

        result=""
        
        # autorizacao.
        server_timeout,client_timeout,client_username\
            =http_util.http_authorization(global_data.host_auth\
            ,global_data.access_token\
            ,http_util.http_get_token_in_header(web))    

        # resposta.
        if server_timeout<=0 or client_timeout<=0:
            web.ctx.status='401 Unauthorized'
            return
        
        # Sinalizador. 
        # Permite apenas uma transferencia em andamento (dev.write) por vez.
        if not global_data.busy:
#                print "not busy"
            global_data.busy=True
            # falando o texto.
            id_stm=self.to_speakers(client_username)
#            web.debug("id stm = "+id_stm)
            try:
                if id_stm>0:
                    result=xml_util.dict_to_rdfxml(\
                        {"id_resource":id_stm},"tts")
            except:
                web.debug("[ERROR] Nao foi possivel executar e/ou gravar o comando recebido.")
            global_data.busy=False
        else:
            web.debug("[ERROR] busy.")

        return result

    def to_speakers(self,client_username):

        # Lendo dados recebidos (exceto status e id)
        texto=xml_util.key_parent_from_xml(web.data(),'text_to_speech','tts')
        id_stm=0

        # TODO: Validar texto com palavras bloqueadas.
        
        if len(texto) == 0 or (not isinstance(texto, str)):
            web.debug('[INFO] Dados incorretos. Nao foram enviados ao dispositivo.')
            
        else:
            # Speaking
#            print "Speaking"
            if subprocess.call(["espeak","-vpt",texto])==0:
                global_data.tts_id=global_data.tts_id+1
                global_data.resource['text_to_speech']=texto
                
                try:
                    # log no servico stm
                    recurso_rdfxml=xml_util.dict_to_rdfxml(\
                        {"text_to_speech":texto,\
                        "id":global_data.tts_id,\
                        "client_username":client_username}, "tts")
                    xml_response=http_util.http_request('post'\
                        ,global_data.host_stm,"/"\
                        ,None,global_data.access_token,recurso_rdfxml)
                    id_stm=int(xml_util.key_parent_from_xml\
                        (xml_response,"id_resource","stm"))
    #                print xml_response
                except:
                    id_stm=0
                
            else:
                web.debug("[ERROR] Ao chamar espeak pelo subprocess.")

        return id_stm

        

#application = web.application(urls, globals()).wsgifunc()

if __name__ == "__main__":
    
    
    global_data.tts_id=0
    global_data.busy=False
    global_data.access_token="anonymous"
    global_data.realm="realm@som4r.net"
    global_data.user="tts"
    global_data.passwd="123456"
    global_data.host_auth="localhost:8012"
    global_data.host_stm="localhost:8098"
    global_data.resource={ \
        "text_to_speech" : "", \
        "id" : 0\
        }
    
    # autenticando este servidor.
    # authenticate and get token.
    global_data.access_token,xml_resource\
        =http_util.http_authentication(global_data.realm\
        ,global_data.host_auth,global_data.user,global_data.passwd)
#    print "token="+str(global_data.access_token)
    if global_data.access_token is None \
        or (not isinstance(global_data.access_token,str)):
        print "[ERROR] cannot get token."

    app.run()
