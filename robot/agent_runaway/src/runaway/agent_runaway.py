#!/usr/bin/env python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Oct 2, 2011 2:47:28 PM$"

import time
import thread
import web
import numpy
import math

import global_data
import xml_util
import robot_util
import http_util


sleep_thread_ms = 50
subsumption_cycles_timeout = 3
min_distance_cm = 70
max_kinect_response_time_ms = 500


urls = (
    '/(.*)', 'index'
)
app = web.application(urls, globals())


class index:
    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # ==========

    def GET(self, name):
        web.header('Content-Type', 'application/xml')
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

        web.debug("POST time: " + str(int(time.time() * 1000) - t0) + "ms")

        return xml_util.dict_to_rdfxml(global_data.resource, 'subsumption')



def run_thread (threadname, sleeptime_ms):
    """This is the thread function to be invoked."""
    global min_distance_cm,max_kinect_response_time

    while True:
        # Verifica o estado da inibicao.
        # Agente foi inibido?
        if len(global_data.resource['inhibited_by']) > 0:
            # Verifica o timeout da inibicao.
            if (int(time.time()*1000) \
                - global_data.resource['inhibited_timestampms'] \
                > (subsumption_cycles_timeout * sleep_thread_ms)):
                # Reset.
                global_data.resource['inhibited_by'] = ""
                global_data.resource['inhibited_timestampms'] = 0
                print "reset done"
                # ToDo: log do reset no servico stm
            else:
                print "inhibited_by: " + global_data.resource['inhibited_by']
                # ToDo: log do bloqueio no servico stm

        # Agente nao foi inibido.
        # Executar processo do agente.
        if len(global_data.resource['inhibited_by']) == 0:

            t0 = int(time.time() * 1000)
            t_ = int(time.time() * 1000)
            
            # Lendo servico kinect.
            xml_kinect=http_util.http_request('get'\
                ,global_data.host_kinect,"/"\
                ,None,global_data.access_token,None)
            try:
                closest=int(xml_util.key_parent_from_xml\
                    (xml_kinect,'depth_closest_cm','kinect'))
            except:
                closest=0

#            print "Time to get kinect data: " + str(int(time.time() * 1000) - t0) + "ms"
#            print "closest = " + str(closest)

            # Se existe obstaculos num raio minimo.
            # Ou se demorou mais que o tempo maximo para ler os dados do kinect.
            if closest < min_distance_cm \
              or (int(time.time() * 1000) - t0) > max_kinect_response_time_ms:

                t0 = int(time.time() * 1000)

                # Lendo sensor kinect - novamente
                xml_kinect=http_util.http_request('get'\
                    ,global_data.host_kinect,"/"\
                    ,None,global_data.access_token,None)
                try:
                    closest1=int(xml_util.key_parent_from_xml\
                        (xml_kinect,'depth_closest_cm','kinect'))
                except:
                    closest1=0
                
#                print "closest again = " + str(closest1)
                closest_med = int((closest + closest1)/2)
                
                closest_is=(closest_med<min_distance_cm)
                kinect_timeout=((int(time.time()*1000)-t0)\
                    >max_kinect_response_time_ms)

                if closest_is or kinect_timeout:

                    t0 = int(time.time() * 1000)

                    global_data.id_supress = ""

                    # Lendo status do veiculo.
                    # Lendo a velocidade atual.
                    xml_veiculo=http_util.http_request('get'\
                        ,global_data.host_veiculo,"/"\
                        ,None,global_data.access_token,None)            
                    try:
                        velocity=int(xml_util.key_from_xml\
                            (xml_veiculo, "velocidade"))
                        direction=int(xml_util.key_from_xml\
                            (xml_veiculo, "direcao"))
                    except:
                        velocity = -1
                        direction = -1
                        
                    movement_on=(velocity>0)
                    movement_ahead=(velocity>0 \
                        and (direction in [1,2,3]))
                    movement_right_left=(velocity>0 \
                        and (direction in [4,6]))
                    movement_rotation=(velocity>0 \
                        and (direction in [7,9]))
                    movement_maybe=(velocity<0 or direction<0)
                        
                    if movement_maybe or movement_ahead or movement_right_left:
                        
                        # Subsuncao da entrada (supressao) do servico veiculo.
                        recursoXml=xml_util.dict_to_rdfxml(\
                            {"supressed_by":"agent_runaway"},'subsumption')
                        # Enviar comando ao veiculo.
                        xml_kinect=http_util.http_request('post'\
                            ,global_data.host_veiculo,"/"\
                            ,None,global_data.access_token,recursoXml)

                        global_data.id_supress=xml_util.key_parent_from_xml(\
                            xml_kinect,"id_supress","subsumption")
                        print "supressao com sucesso: " + global_data.id_supress
                        print "Parando veiculo..."
                        
                        # STOP
                        recursoXml = """<VeiculoRO> 
                            <id_timeout>1</id_timeout> 
                            <direcao>5</direcao> 
                            <tempo>0</tempo> 
                            <velocidade>0</velocidade> 
                            <id_supress>""" + str(global_data.id_supress) + """</id_supress> 
                            </VeiculoRO>"""
            #                web.debug(recursoXml)
                        # Enviar comando.
                        
                        # Enviar comando ao veiculo.
                        xml_response=http_util.http_request('post'\
                            ,global_data.host_veiculo,"/"\
                            ,None,global_data.access_token,recursoXml)

#                        print "Time to post stop command: " \
#                            + str(int(time.time() * 1000) - t0) + "ms"

                        t0 = int(time.time() * 1000)
                
                        if kinect_timeout:
                            print "Parada preventiva devido a lentidao no acesso ao kinect"
                            # Parada total.
                        else:
                            print "Parada devido a objeto muito proximo"
                            
                            try:
                                repulsive_module=float(xml_util.key_from_xml(\
                                    xml_kinect,"repulsive_module"))
                                angle_rad=float(xml_util.key_from_xml(\
                                    xml_kinect, "angle_rad"))
                            except:
                                repulsive_module=0
                                angle_rad=0
                                
                            # calculando angulo "final" de repulsao.
                            if angle_rad >= 0:
                                angle_back = angle_rad - numpy.pi
                            else:
                                angle_back = numpy.pi + angle_rad
                            # calculando componentes da repulsao "final".
                            rfx = repulsive_module * math.cos(angle_back)
                            rfy = repulsive_module * math.sin(angle_back)
                            # calculando resultante entre a repulsao final e um vetor
                            #  de mesmo modulo com angulo zero (em frente).
                            frx = rfx + repulsive_module
    #                        fry = rfy + 0
                            try:
                                angle_to_go_rad=math.atan(rfy / frx)
                                angle_to_go_deg=angle_to_go_rad*360.0/(2*numpy.pi)
                            except:
                                angle_to_go_rad,angle_to_go_deg=0,0
                            
                            module_to_go = math.sqrt(frx**2 + rfy**2)

    #                        # aplicando a "forca repulsiva" resultante.
    #                        # rodando no maximo 10 graus por vez.
    #                        if angle_to_go_deg > 0:
    #                            angle_deg_now = min(10, angle_to_go_deg/3)
    #                        elif angle_to_go_deg <= 0:
    #                            angle_deg_now = max(-10, angle_to_go_deg/3)
    #                        rotate_vehicle(deg_to_millisec(angle_deg_now))
    #                        print "rotating " + str(angle_deg_now) + " for " + str(angle_to_go_deg)

                            if movement_ahead or movement_right_left:
                                rotate_angle_deg=int(angle_to_go_deg/3)
                                robot_util.rotate_vehicle_deg(rotate_angle_deg\
                                    , url_wsrest_veiculo\
                                    , str(global_data.id_supress))
                                print "rotation = " + str(angle_to_go_deg) \
                                    +" -> "+str(rotate_angle_deg) +" deg"

#                                # postando comando anterior ao desvio
#                                recursoXml = "<VeiculoRO>\
#                                    <id_timeout>1</id_timeout>\
#                                    <direcao>"\
#                                    + xml_util.key_from_xml(xml_veiculo, "direcao")\
#                                    + "</direcao>\
#                                    <tempo>"\
#                                    + xml_util.key_from_xml(xml_veiculo, "tempo")\
#                                    + "</tempo> \
#                                    <velocidade>"\
#                                    + xml_util.key_from_xml(xml_veiculo, "velocidade")\
#                                    + "</velocidade> \
#                                    <id_supress>" + global_data.id_supress + "</id_supress> \
#                                    </VeiculoRO>"
#                                # Enviar comando.
#                                conn = httplib.HTTPConnection(url_wsrest_veiculo)
#                                conn.request("POST", "/", recursoXml)
#                                response = conn.getresponse()
#                                conn.close()
#                                xml_veiculo

                            # ToDo:
                            # avancar/retroceder proporcionalmente ao modulo da resultante.


#            print "Time of thread run: " \
#                + str(int(time.time() * 1000) - t_) + "ms"

        # Se o tempo total de execucao
        # demorou igual ou mais q o tempo de sleep, dorme apenas 10ms.
        sleeptime_now = 10 \
            if (int(time.time() * 1000) - t_) >= sleep_thread_ms \
            else sleeptime_ms
        time.sleep(sleeptime_now/1000)

    thread.interrupt_main()


if __name__ == "__main__":

    global_data.id_supress = ""
    global_data.resource = {
        "inhibited_by" : "", \
        "inhibited_timestamp" : ""
    }

    global_data.access_token="anonymous"
    global_data.realm="realm@som4r.net"
    global_data.user="runaway"
    global_data.passwd="123456"
    global_data.host_auth="localhost:8012"
    global_data.host_stm="localhost:8098"
    global_data.host_kinect="localhost:8094"
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

