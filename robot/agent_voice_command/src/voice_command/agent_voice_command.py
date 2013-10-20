#! /usr/bin/python

__author__="marcus"
__date__ ="$Jun 24, 2011 11:22:50 AM$"


import web
import time
import thread

import global_data
import xml_util
import http_util


urls=(
    '/(.*)', 'index'
    )


class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    def GET(self, name):

        #TODO: ????? Subsuncao com classe = servico veiculo.
                
        web.header('Content-Type', 'application/xml')

        # autorizacao.
        server_timeout,client_timeout,client_username\
            =http_util.http_authorization(global_data.host_auth\
            ,global_data.access_token\
            ,http_util.http_get_token_in_header(web))    
        # resposta.
        if server_timeout<=0 or client_timeout<=0:
            web.ctx.status = '401 Unauthorized'
            return

#        tg = int(time.time() * 1000)
#
#        tg = int(time.time() * 1000) - tg
#        web.debug('GET total time: ' + str(tg) + " ms")

        return xml_util.dict_to_rdfxml(global_data.resource,'voice_command')
    
    def POST(self, name):

        return '<status>TODO: subsumption</status>'
    

# thread function.
def run_thread (threadname, sleeptime_ms): 

    while True:
        #TODO: Verifica o estado da inibicao.

        # Agente nao foi inibido.
        # Executar processo do agente.
        if global_data.subsumption_inhibited==False:
            
            # ler ultima palavra/frase do servico listen.
            xml_response=http_util.http_request('get'\
                ,global_data.host_listen,"/"\
                ,None,global_data.access_token,None)
            listen_command=xml_util.key_parent_from_xml(xml_response,'result','listen')
            listen_uttid=xml_util.key_parent_from_xml(xml_response,'uttid','listen')            
            
            # processando resposta.
            # verifica se tem texto (nao esta vazio),
            # ou se ja processou o comando,
            # TODO: ou se faz mais de 5 segundos.
            if len(listen_command)>0 and global_data.last_uttid!=listen_uttid:
                listen_command=listen_command.upper()
                tts_data=""
                veiculo_data=""
                active_before=global_data.active
                ignore_command=True   # ignorando comandos nao cadastrados
                global_data.last_uttid=listen_uttid

                # verifica se o comando eh para ativar/deativar o comando de voz.
                if listen_command in ['VOICE','COMMAND','VOICE COMMAND']:
                    
                    # comando de voz esta ativo?
                    if not global_data.active:  # Nao esta ativo.
                        
                        # confirma que quer ligar.
                        # chamando servico tts
                        recurso_rdfxml=xml_util.dict_to_rdfxml(\
                            {"text_to_speech":"ativar o comando de voz?"}, "tts")
                        xml_response=http_util.http_request('post'\
                            ,global_data.host_tts,"/"\
                            ,None,global_data.access_token,recurso_rdfxml)
                            
                        # procurando resposta durante 5 segundos, 3x por seg.
                        t_now=int(time.time()*10000)
                        while (t_now>0):
                            time.sleep(0.250)
                            waiting=(int(time.time()*10000)-t_now)
                            if waiting>wait_for_response_s*10000:
                                t_now=0
                            else:
                                # ler ultima palavra/frase do servico listen.
                                xml_response=http_util.http_request('get'\
                                    ,global_data.host_listen,"/"\
                                    ,None,global_data.access_token,None)
                                listen_command=xml_util.key_parent_from_xml(xml_response,'result','listen')
                                listen_uttid=xml_util.key_parent_from_xml(xml_response,'uttid','listen') 
                                # palavra nova?
                                if len(listen_command)>0 and listen_uttid>global_data.last_uttid:
                                    global_data.last_uttid=listen_uttid
                                    listen_command=listen_command.upper()
                                    if listen_command in ['YES', 'OK']:
                                        global_data.active=True     # Ativando agente. 
                                        tts_data='comando de voz ativado.'
                                        break
                            
                            
                    else:   # Sim, esta ativo.      
                        #TODO: verificar se o comando eh para desativar o comando de voz.
                        global_data.active=False     # Desativando agente. 
                        tts_data='comando de voz desativado'
                        
                # se nao houve ativacao ou desativacao do comando de voz,
                # e o agente esta ativo, entao tentar processar o comando.
                if global_data.active==active_before and global_data.active:

                    direcao = "5"
                    velocidade = "0"
                    # Direcao e/ou velocidade
                    if listen_command == "STOP":
                        direcao = "5"
                        ignore_command = False
                    elif listen_command == "AHEAD":
                        direcao = "2"
                        ignore_command = False
                    elif listen_command == "BACK":
                        direcao = "8"
                        ignore_command = False
                    elif listen_command == "RIGHT":
                        direcao = "6"
                        ignore_command = False
                    elif listen_command == "LEFT":
                        direcao = "4"
                        ignore_command = False
                    elif listen_command in ["AHEAD RIGHT", "RIGHT AHEAD"]:
                        direcao = "3"
                        ignore_command = False
                    elif listen_command in ["AHEAD LEFT", "LEFT AHEAD"]:
                        direcao = "1"
                        ignore_command = False
                    elif listen_command in ["FASTER","SLOWER"]:
                        # Lendo a velocidade atual.
                        xml_veiculo=http_util.http_request('get'\
                            ,global_data.host_veiculo,"/"\
                            ,None,global_data.access_token,None)            
                        try:
                            direcao=xml_util.key_from_xml(xml_veiculo,"direcao")
                            velocidade=xml_util.key_from_xml(xml_veiculo,"velocidade")
                #            web.debug("velocidade antes = " + velocidade)
                            if listen_command=="FASTER":
                                velocidade = str(min(int(velocidade) + 10, 100))
                            else:
                                velocidade = str(max(int(velocidade) - 10, 70))
                #            web.debug("velocidade depois = " + velocidade)
                            ignore_command = False
                        except:
                            web.debug('[ERROR] ao tentar ler estado atual do veiculo.')

                    # o comando foi reconhecido.
                    if not ignore_command:
                        # Velocidade
                        # Se parar entao velocidade zero.
                        if (int(direcao) == 5 or int(direcao) == 0):
                            velocidade = "0"
                        # Senao se velocidade zero entao velocidade baixa.
                        elif int(velocidade) == 0:
                            velocidade = "80"

                #        web.debug("velocidade final = " + velocidade)

                        # Montando recurso
#                       #TODO: recurso_xml=xml_util.dict_to_rdfxml(\
#                            {},"vehicle")
                        recursoXml = "<VeiculoRO>" \
                            + "<direcao>" + direcao + "</direcao>" \
                            + "<velocidade>" + velocidade + "</velocidade>" \
                            + "<id_timeout>" + str(int(time.time() * 100)) + "</id_timeout>" \
                            + "</VeiculoRO>"
                        #web.debug("recurso OUT = " + recursoXml)
                        
                        veiculo_data="velocity:"+str(velocidade)+",direction:"+str(direcao)
                        
                        # Enviar comando.
                        xml_response=http_util.http_request('post'\
                            ,global_data.host_veiculo,"/"\
                            ,None,global_data.access_token,recursoXml)
                        
#                    else:
#                        web.debug("post ok, command ignored")
            
                                    
                # se houve ativacao ou desativacao do comando de voz,
                # ou o agente esta ativo, entao deve registrar no servico STM.
                if global_data.active!=active_before or (not ignore_command):
                    global_data.command_id=global_data.command_id+1

                    # log no servico stm
                    resource_rdfxml = xml_util.dict_to_rdfxml(\
                        {"command":listen_command,\
                        "tts":tts_data,"vehicle":veiculo_data,\
                        "id":global_data.command_id}, "voice_command")
                    xml_response=http_util.http_request('post'\
                        ,global_data.host_stm,"/"\
                        ,None,global_data.access_token,recurso_rdfxml)                
                
                # tts?
                if len(tts_data)>0:
                    # chamando servico tts
                    resource_rdfxml = xml_util.dict_to_rdfxml(\
                        {"text_to_speech":tts_data}, "tts")
                    xml_response=http_util.http_request('post'\
                        ,global_data.host_tts,"/"\
                        ,None,global_data.access_token,recurso_rdfxml)                    
                    
        # dormir.
        time.sleep(global_data.sleep_thread_ms/1000.)

    thread.interrupt_main()         
    


#application = web.application(urls, globals()).wsgifunc()

application = web.application(urls, globals())


if __name__ == "__main__":
    
    global_data.sleep_thread_ms=250
    global_data.wait_for_response_s=4
    global_data.command_id=0
    global_data.active=False
    global_data.subsumption_inhibited=False
    global_data.last_uttid="0"
    global_data.access_token="anonymous"
    global_data.user=""
    global_data.passwd=""
    global_data.host_auth="localhost:8012"
    global_data.host_veiculo="localhost:8080"
    global_data.host_listen="localhost:8090"
    global_data.host_stm="localhost:8098"
    global_data.host_tts="localhost:8096"
    global_data.subsumption = {
        "inhibited_by" : "", \
        "inhibited_timestamp_ms" : ""
    }
    global_data.resource = {
        "command" : "", \
        "id" : 0 \
    }
    
    # authenticate and get token.
    global_data.access_token,xml_resource\
        =http_util.http_authentication(global_data.realm\
        ,global_data.host_auth,global_data.user,global_data.passwd)
#        print "token="+str(global_data.access_token)
    if global_data.access_token is None \
        or (not isinstance(global_data.access_token,str)):
        print "[ERROR] cannot get token."


    thread.start_new_thread(run_thread, ("Thread1", sleep_thread_ms))

    application.run()

#    try:
#        while 1:
#            pass
#    except:
#        print "Exiting...."
