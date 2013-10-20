#!/usr/bin/env python
# -*- coding: cp860 -*-

__author__="marcus"
__date__ ="$Aug 28, 2011 5:22:46 PM$"


import httplib
import os
import time

snapshot_faces_dir = os.environ['HOME'] + "/robot_/faces/"

class HelloPeople:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    url_wsr_face_detection = "localhost:8091"
    url_wsr_face_recognition = "localhost:8097"
    url_wsr_tts = "localhost:8096"
    faces_dir = os.environ['HOME'] + "/robot_/faces/"

    # ============ Final da Inicializacao unica por classe =================

    def run_loop(self):

        while True:
            print "procurando pessoas"
            # Lendo sensor de faces.
            conn = httplib.HTTPConnection(self.url_wsr_face_detection)
            conn.request("GET", "/")
            response = conn.getresponse()
            xml_response = response.read()
            conn.close()
            num_faces = int(self.key_from_xml(xml_response, "num_faces_"))
            id_image = self.key_from_xml(xml_response, "id_")
            # Se encontrou faces segue procurando identificar cada face.
            for i in range(num_faces):
                print "face nro: "+str(i)

                # Chamando servico de identificacao de faces.
                recursoXml = "<FaceRecognition><local_face>" \
                    + (snapshot_faces_dir + id_image + "_face" + str(i) + ".png") \
                    + "</local_face> \
                    <threshold>1</threshold> \
                    </FaceRecognition>"
    #                web.debug(recursoXml)
                # Enviar comando.
                conn = httplib.HTTPConnection(self.url_wsr_face_recognition)
                conn.request("POST", "/", recursoXml)
                response = conn.getresponse()
                xml_response = response.read()
                conn.close()

                matches = self.key_from_xml(xml_response, "matches")
                distance = self.key_from_xml(xml_response, "dist")
                filename_split = matches.split("__")
                if len(filename_split)>1: # Existe os caracteres "__" no filename.
                    name = filename_split[0]
                    print "Identificacao positiva: " + name + " dist = " + distance

                    # Chamando servico tts para chamar o nome da pessoa identificada.
                    recursoXml = "<TtsRO><texto>" \
                        + "olá " + name + "?" \
                        + "</texto> \
                        </TtsRO>"
        #                web.debug(recursoXml)
                    # Enviar comando.
                    conn = httplib.HTTPConnection(self.url_wsr_tts)
                    conn.request("POST", "/", recursoXml)
                    response = conn.getresponse()
#                    xml_response = response.read()
                    conn.close()

                    # ToDo:
                    # Aguardar resposta

                    # pausa entre frases.
                    time.sleep(0.5)

            if num_faces == 0:
                time.sleep(1)

    def key_from_xml(self, xml, key):
        result = ""
        inicio = xml.find("<" + key + ">")
        if inicio >= 0:
            final = xml.find("</" + key + ">")
            if inicio >= 0 and final > inicio:
                result = xml[inicio + len(key) + 2 : final]
        return result



if __name__ == "__main__":
#    print "Hello People"
    app = HelloPeople()
    app.run_loop()