#! /usr/bin/python

__author__="marcus"
__date__ ="$Oct 30, 2010 11:59:41 AM$"

import web
import serial
import subprocess

import xml_util
import http_util
import global_data


urls = (
        '/(.*)', 'index'
        )

#web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

recurso = { \
    "latitude" : "", \
    "longitude" : "", \
    "altitude" : "", \
    "velocity" : "", \
    "angle" : "", \
    "id" : ""
    }

gps_busy=False
gps_id=0


# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
    #, initializer={'logged_in': False})

class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # Inicializando GPS
    #ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)


    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):

        web.header('Content-Type', 'application/xml')
        global recurso,gps_busy
        
        # autorizacao.
        server_timeout,client_timeout,client_username\
            =http_util.http_authorization(global_data.host_auth\
            ,global_data.access_token\
            ,http_util.http_get_token_in_header(web))    
        # resposta.
        if server_timeout<=0 or client_timeout<=0:
            web.ctx.status='401 Unauthorized'
            return
        
        recurso['cached']="true"
        recurso["error"]="false"
        
        if not gps_busy:
            gps_busy=True
            
            try:
                # lendo o dispositivo.
                self.read_serial()

                recurso['client_username']=client_username
                recurso['cached']="false"

                # log no servico stm
                resource_rdfxml=xml_util.dict_to_rdfxml(recurso,"gps")
                xml_response=http_util.http_request('post'\
                    ,global_data.host_stm,"/"\
                    ,None,global_data.access_token,resource_rdfxml)
            except:
                recurso["error"]="true"
                
            gps_busy=False

        return xml_util.dict_to_rdfxml(recurso,"gps")

    def read_serial(self):
	# Inicializando GPS 
	# 20110328 colocada aqui porque dava erro quando colocada na inicializacao (comentado acima).
    	ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        
        global recurso, gps_id
        recurso['latitude'] = '-3.75'
        recurso['longitude'] = '-38.53'
        recurso['altitude'] = '0'
        recurso['angle'] = '0'
        recurso['velocity'] = '0'
        recurso['id'] = gps_id
        for i in range(1, 8):   # 7 mensagens por ciclo
            linha = ser.readline()
            lista = linha.split(',')
            if lista[0] == '$GPGGA':
                recurso['altitude'] = lista[9]
#                recurso['id'] = str(int(time.time() * 100))
            
            if lista[0] == '$GPRMC':
                temp = float(lista[3]) / 100
                graus = int(temp)
                minutos = temp - graus  # somente a parte decimal
                minutos = minutos * 10 / 6    # convertendo para milesimo de minuto
                temp = graus + minutos
                temp = temp if (lista[4] == "N") else (temp * (-1))
                recurso['latitude'] = str(temp)
                temp = float(lista[5]) / 100
                graus = int(temp)
                minutos = temp - graus  # somente a parte decimal
                minutos = minutos * 10 / 6    # convertendo para milesimo de minuto
                temp = graus + minutos
                temp = temp if (lista[6] == "E") else (temp * (-1))
                recurso['longitude'] = str(temp)
                recurso['angle'] = lista[8]
                recurso['velocity'] = lista[7]
	
	ser.close()

        gps_id=gps_id+1
        

    def __done__(self):
        # Liberando recursos
        web.debug('[DONE] wsrest_gps - Encerrando execucao.')
        #self.ser.close()


application = web.application(urls, globals())

#application = web.application(urls, globals()).wsgifunc()


if __name__ == "__main__":
    
    # Permissoes de acesso ao GPS
    subprocess.call(["sudo","chmod","666","/dev/ttyUSB0"])
    
    global_data.access_token="anonymous"
    global_data.realm="realm@som4r.net"
    global_data.user="gps"
    global_data.passwd="123456"
    global_data.host_auth="localhost:8012"
    global_data.host_stm="localhost:8098"
    
    # autenticando este servidor.
    # authenticate and get token.
    global_data.access_token,xml_resource\
        =http_util.http_authentication(global_data.realm\
        ,global_data.host_auth,global_data.user,global_data.passwd)
#    print "token="+str(global_data.access_token)
    if global_data.access_token is None \
        or (not isinstance(global_data.access_token,str)):
        print "[ERROR] cannot get token."
        
        
    application.run()