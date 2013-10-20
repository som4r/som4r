# To change this template, choose Tools | Templates
# and open the template in the editor....

import httplib

def rotate_vehicle_deg(rotation_deg, url_wsrest_veiculo, id_supress=""):
    # converte de graus para ms.
    rotation_ms = deg_to_millisec(rotation_deg)
    # Comando girar.
    if rotation_ms != 0:
        direcao_rotacao = 7 if rotation_ms >= 0 else 9
        # Preparando comando girar com velocidade minima.
        recursoXml = "<VeiculoRO> \
            <id_timeout>1</id_timeout> \
            <direcao>" + str(direcao_rotacao) + "</direcao> \
            <tempo>" + str(abs(rotation_ms)) + "</tempo> \
            <velocidade>80</velocidade>"
        if len(id_supress)>0:
            recursoXml=recursoXml\
                +"<id_supress>" + id_supress + "</id_supress>" 
        recursoXml=recursoXml+"</VeiculoRO>"
        # Enviar comando.
        conn = httplib.HTTPConnection(url_wsrest_veiculo)
        conn.request("POST", "/", recursoXml)
        response = conn.getresponse()
        conn.close()

def deg_to_millisec(rotation_deg):
    if abs(rotation_deg) < 1:
        tempo_giro = 0      # ignorando movimento menor q +-1 grau.
    elif rotation_deg > 0:
        tempo_giro = 10590   # p/esquerda
    elif rotation_deg < 0:
        tempo_giro = 10680   # p/direita

    return int((rotation_deg/360.0)*tempo_giro)