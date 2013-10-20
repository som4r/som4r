#!/usr/bin/python

__author__="marcus"
__date__ ="$Jul 10, 2011 9:39:16 PM$"

import web
import StringIO
import httplib

urls = (
    '/(.*)', 'index'
)

web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

recurso = { \
    "status" : "ready", \
    "action" : "", \
    "id" : 0 \
    }

class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    url_wsrest_veiculo = "192.168.1.107:8080"
    url_wsrest_fuzzy_follow = "192.168.1.107:8093"
    url_wsrest_kinect = "192.168.1.107:8094"

    # ============ Final da Inicializacao unica por classe =================
    def GET(self, name):
        web.header('Content-Type', 'application/xml')
        global recurso

        if not name:
            name = 'World......'
        return self.to_xml(recurso)


    def POST(self, name):

        global recurso
        # Atualizando recurso com dados do post.
        self.from_xml(web.data())

        # Sinalizador. Permite apenas uma transferencia em andamento por vez.
#        if recurso['status'] == 'ready':
        web.debug("POST...start")
        self.explore()
        web.debug("POST...end")
        status_returned = recurso['status']
#        elif recurso['action'] == 'cancel':
#            self.explore()
#            status_returned = 'calceled'
#        else:
#            status_returned = 'busy'

        recurso['status'] = 'ready'
        return '<status>' + status_returned + '</status>'

    def explore(self):
        global recurso
        finish = False
        # Loop principal.
        # inicia indo em frente ate chegar proximo (+-1m) de um obstaculo.
        # A partir dai ele decide pela maior area ate nao ter obstaculos proximos.
        # Quando existem obstaculos proximos o movimento, rotacao e avanco, sao
        # decididos usando logica fuzzy (Fuzzy_Follow webservice).
        # Quando nao existem obstaculos a direcao preferencial eh em frente.
        while True:
            # Saida forcada
            if recurso['action'] == 'cancel':
                finish = True
                break

            # Lendo a direcao e velocidade atual.
#            conn = httplib.HTTPConnection(self.url_wsrest_veiculo)
#            conn.request("GET", "/")
#            response = conn.getresponse()
#            xml_veiculo = response.read()
#            conn.close()
#            direction = self.key_from_xml(xml_veiculo, "direcao")
#            velocity = self.key_from_xml(xml_veiculo, "velocidade")

            # Lendo sensor kinect
            conn = httplib.HTTPConnection(self.url_wsrest_kinect)
            conn.request("GET", "/")
            response = conn.getresponse()
            xml_kinect = response.read()
            conn.close()
            closest = int(self.key_from_xml(xml_kinect, "depth_closest"))

            # Se existe obstaculos num raio de +-1m
            if closest < 700:
                # entao deve usar a sugestao do servico (best_direction).
                best_direction = float(self.key_from_xml(xml_kinect, "best_direction"))
                cols_image = float(self.key_from_xml(xml_kinect, "screen_cols"))
                relative_col_pos = int((best_direction / cols_image) * 100.0)
                best_depth = int(self.key_from_xml(xml_kinect, "best_depth"))
                # Preparando comando para postar ao servico fuzzy_follow.
                recursoXml = "<FuzzyFollow> \
                    <id>1</id> \
                    <relative horizontal position>" + str(relative_col_pos) + \
                    "</relative horizontal position> \
                    <distance>" + str(best_depth) + "</distance> \
                    </FuzzyFollow>"
#                web.debug("FuzzyFollow " + str(best_direction) + "  "\
#                    + str(cols_image) + "  " + str(relative_col_pos) \
#                    + "  " + str(best_depth))
#                web.debug(recursoXml)
                # Enviar comando.
                conn = httplib.HTTPConnection(self.url_wsrest_fuzzy_follow)
                conn.request("POST", "/", recursoXml)
                response = conn.getresponse()
                conn.close()

            # Senao
            else:
                # vai em frente.
                # Preparando comando avancar com velocidade minima.
                recursoXml = "<VeiculoRO> \
                    <id_timeout>1</id_timeout> \
                    <direcao>2</direcao> \
                    <tempo>" + str(2000) + "</tempo> \
                    <velocidade>80</velocidade> \
                    </VeiculoRO>"
                web.debug(recursoXml)
                # Enviar comando.
                conn = httplib.HTTPConnection(self.url_wsrest_veiculo)
                conn.request("POST", "/", recursoXml)
                response = conn.getresponse()
                conn.close()

            # Final do loop


        recurso['status'] = 'ready'
        return '<status>' + ('post ok' if finish == False else 'post canceled') \
            + '</status>'

    def key_from_xml(self, xml, key):
        result = ""
        inicio = xml.find("<" + key + ">")
        if inicio >= 0:
            final = xml.find("</" + key + ">")
            if inicio >= 0 and final > inicio:
                result = xml[inicio + len(key) + 2 : final]
        return result

    def from_xml(self, xml):
        #print xml
        # ToDo: Remover tudo que nao estiver dentro da tag do recurso
        global recurso
        recurso['status'] = 'reading xml data'
        for item in recurso.items():
            key, value = item
            inicio = xml.find("<" + key + ">")
            if inicio >= 0:
                final = xml.find("</" + key + ">")
                if inicio >= 0 and final > inicio:
                    # Ignorando atributos 'status' e 'id'.
                    if key != 'status' and key != 'id': # Ignorando atributo 'status'.
                        stringXml = xml[inicio + len(key) + 2 : final]
                        if len(stringXml) > 0: # Ignorando chaves vazias.
                            # Diferenciando valor (string ou int)
                            if isinstance(recurso[key], str):
                                recurso[key] = stringXml
                            else:
                                recurso[key] = int(stringXml)

    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
#        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  "Explorer")

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % "Explorer")
        stream.seek(0)
        return stream.read()


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
