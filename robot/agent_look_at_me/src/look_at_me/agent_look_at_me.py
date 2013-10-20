#!/usr/bin/env python

__author__="marcus"
__date__ ="$Nov 21, 2011 10:01:36 PM$"


import time
import thread
import web
import numpy
import math

import global_data
import xml_util
import robot_util
import http_util


sleep_thread_ms = 250
min_x_size_of_face_px = 30
time_without_movement_ms = 5000#60000

urls = (
    '/(.*)', 'index'
)

app = web.application(urls, globals())


class index:
    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

#    # Conectando com bd.
#    db = db_util.connect()

    # ==========

    def GET(self, name):
        web.header('Content-Type', 'application/xml')

        if len(global_data.resource['inhibited_by']) > 0:
            # Verifica o timeout da inibicao.
            if (int(time.time()*1000)-global_data.resource['inhibited_timestampms']\
                > time_without_movement_ms):
                # Reset.
                global_data.resource['inhibited_by'] = ""
                global_data.resource['inhibited_timestampms'] = 0
                print "reset done"
                # Gravando acao de reset.
                # log no servico stm
                resource_rdfxml=xml_util.dict_to_rdfxml\
                    ({"inhibited_reset_after_ms":time_waiting}\
                    , 'subsumption')
                xml_response=http_util.http_request('post'\
                    ,global_data.host_stm,"/"\
                    ,None,global_data.access_token\
                    ,resource_rdfxml)
                    
        return xml_util.dict_to_rdfxml(global_data.resource, 'subsumption')

    def POST(self, name):
        t0 = int(time.time() * 1000)

        # reading parameters (supress, inhibit)
#        xml = xml_util.key_parent_from_xml(web.data(), 'supressed_by', 'subsumption')
#        if len(xml) > 0:
#            global_data.resource['supressed_by'] = xml
#            global_data.resource['supressed_timestampms'] = int(time.time()*1000)
        xml = xml_util.key_parent_from_xml(web.data(), 'inhibited_by', 'subsumption')
        if len(xml) > 0:
            global_data.resource['inhibited_by'] = xml
            global_data.resource['inhibited_timestampms'] = int(time.time()*1000)
            # Gravando subsuncao.
            # log no servico stm
            resource_rdfxml=xml_util.dict_to_rdfxml\
                (global_data.resource,'subsumption')
            xml_response=http_util.http_request('post'\
                    ,global_data.host_stm,"/"\
                    ,None,global_data.access_token\
                    ,resource_rdfxml)
                    
        web.debug("POST time: " + str(int(time.time() * 1000) - t0) + "ms")

        return xml_util.dict_to_rdfxml(global_data.resource,'subsumption')



def run_thread (threadname, sleeptime_ms):
    """This is the thread function to be invoked."""
    global min_x_size_of_face_px,time_without_movement_ms

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
                # Gravando acao de reset.
                db_util.persist_resource(self.db, "agent_look_at_me"\
                    , xml_util.dict_to_rdfxml(\
                    {"inhibited_reset_after_ms":time_waiting}\
                    , 'subsumption'))
            else:
                print "inhibited_by: " + global_data.resource['inhibited_by']
                # ToDo: log do bloqueio no servico stm

        # Agente nao foi inibido.
        # Executar processo do agente.
        if len(global_data.resource['inhibited_by']) == 0:

            t0 = int(time.time() * 1000)
            t_ = int(time.time() * 1000)

#            print "procurando faces"
            # Lendo servico sensor de faces.
            xml_response=http_util.http_request('get'\
                ,global_data.host_face_detect,"/"\
                ,None,global_data.access_token,None)

            # Verificando o tempo que nao eh detectado um movimento no robo.
            # Lendo status do veiculo N vezes.
            for i in range(2):
                
                # Lendo status atual.
                xml_veiculo=http_util.http_request('get'\
                    ,global_data.host_veiculo,"/"\
                    ,None,global_data.access_token,None)            
                try:
                    velocity=int(xml_util.key_from_xml\
                        (xml_veiculo, "velocidade"))
                    direction=int(xml_util.key_from_xml\
                        (xml_veiculo, "direcao"))
                except:
                    velocity=-1
                    direction=-1

                if (velocity > 0 and direction not in [0,5]):
                    global_data.time_last_movement_ms=int(time.time()*1000)

            is_active=(int(time.time()*1000)-global_data.time_last_movement_ms \
                >time_without_movement_ms)

            
            # Agente esta ativo.
            if is_active:
#                print "agent is active"
                # Varrendo as faces detectadas
                try:
                    num_faces=int(xml_util.key_parent_from_xml\
                        (xml_response, "num_faces", "face_detect"))
                except:
                    num_faces=0

                resultant_angle_deg=0
                valid_faces=0
                faces_data=numpy.array(numpy.zeros((num_faces,7)))
                # Se encontrou faces, armazena as posicoes para analise futuras.
                for i in range(num_faces):
#                    print "face nro: "+str(i)
                    xml_faces = xml_util.key_parent_from_xml(xml_response\
                        , 'faces', 'face_detect')

                    # Verificando tamanho da face.
                    # Se a face for menor que um limite (em pixels) deve ser ignorada.
                    # porque ou esta longe, ou pode ser um falso positivo.
                    face_sx = int(xml_util.key_from_xml(xml_faces, "face"+str(i)+"_sx"))
                    if face_sx<min_x_size_of_face_px:
                        print "ignoring face - width: " + str(face_sx)
                        continue

                    valid_faces = valid_faces + 1
                    face_sy = int(xml_util.key_from_xml(xml_faces, "face"+str(i)+"_sy"))
                    face_x = int(xml_util.key_from_xml(xml_faces, "face"+str(i)+"_x"))
                    face_y = int(xml_util.key_from_xml(xml_faces, "face"+str(i)+"_y"))
                    # posicao central da imagem
                    face_x_center = int(face_x+(face_sx/2))
                    face_y_center = int(face_y+(face_sy/2))
                    # calcular angulo da face

                    print "face nro: "+str(i)+"  c=( "+str(face_x_center)\
                        +" , "+str(face_y_center)+" )"

                    # mudando intervalo X de [0,640] para [320,-320]
                    a = (-1)*int(face_x_center-320)
                    # calculando theta a partir de A e da constante B.
                    b = 589.366683531
                    theta_rad = math.atan(a/b)
                    theta_deg = theta_rad*360.0/(2*numpy.pi)
                    resultant_angle_deg = resultant_angle_deg + theta_deg
                    print "angulo = " + str(resultant_angle_deg)
                    
                    faces_data[i,0]=theta_deg
                    faces_data[i,1]=face_x
                    faces_data[i,2]=face_y
                    faces_data[i,3]=face_sx
                    faces_data[i,4]=face_sx
                    faces_data[i,5]=face_x_center
                    faces_data[i,6]=face_y_center

                if valid_faces>0:
                    
                    # Maior face, mais proxima?
                    face_index=faces_data[:,3].argmax()
                    closest_angle_deg=faces_data[face_index,0]
                    # ToDo: Olhar para a face quando estiver muito proxima.

                    #resultant_angle_deg = int(resultant_angle_deg / num_faces)
                    resultant_angle_deg=closest_angle_deg
                    # ajuste
#                    ajuste = 5 if resultant_angle_deg>0\
#                        else -5 if resultant_angle_deg<0\
#                        else 0
                    ajuste=0
                    resultant_angle_deg = resultant_angle_deg + ajuste
                    if resultant_angle_deg < -3 or resultant_angle_deg > 3:
                        # Rotating vehicle.
#                        if resultant_angle_deg>10:
#                            resultant_angle_deg=10
#                        elif resultant_angle_deg<(-10):
#                            resultant_angle_deg=-10
                        robot_util.rotate_vehicle_deg(resultant_angle_deg\
                            , url_wsrest_veiculo)
                        print "rotation " + str(resultant_angle_deg)
                        
                    # Gravando acao do agente.
                    # log no servico stm
                    resource_rdfxml=xml_util.dict_to_rdfxml\
                        ({"rotation_deg":str(resultant_angle_deg)}\
                        ,'look_at_me')
                    xml_response=http_util.http_request('post'\
                        ,global_data.host_stm,"/"\
                        ,None,global_data.access_token\
                        ,resource_rdfxml)

        # dormir.
        time.sleep(sleep_thread_ms/1000.)

    thread.interrupt_main()


if __name__ == "__main__":

    global_data.resource={
        "inhibited_by" : "", \
        "inhibited_timestamp" : ""
    }
    
    global_data.time_last_movement_ms=int(time.time()*1000)

    global_data.access_token="anonymous"
    global_data.realm="realm@som4r.net"
    global_data.user="look_at_me"
    global_data.passwd="123456"
    global_data.host_auth="localhost:8012"
    global_data.host_stm="localhost:8098"
    global_data.host_face_detect="localhost:8091"
    global_data.host_veiculo="localhost:8080"
    
    # autenticando este servidor.
    # authenticate and get token.
    global_data.access_token,xml_resource\
        =http_util.http_authentication(global_data.realm\
        ,global_data.host_auth,global_data.user,global_data.passwd)
#    print "token="+str(global_data.access_token)
    if global_data.access_token is None \
        or (not isinstance(global_data.access_token,str)):
        print "[ERROR] cannot get token."
        
        
    thread.start_new_thread(run_thread, ("Thread1", sleep_thread_ms))

    app.run()

#    try:
#        while 1:
#            pass
#    except:
#        print "Exiting...."

