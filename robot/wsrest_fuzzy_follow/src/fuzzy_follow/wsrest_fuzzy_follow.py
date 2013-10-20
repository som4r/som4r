#! /usr/bin/python

__author__="marcus"
__date__ ="$Jul 2, 2011 10:04:55 PM$"


import web
import StringIO
import time
import numpy
import math
import httplib



urls = (
        '/(.*)', 'index'
        )

web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

recurso = { \
    "status" : "ready", \
    "relative horizontal position" : 0, \
    "distance" : 0, \
    "id" : 0 \
    }

# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
    #, initializer={'logged_in': False})

class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    url_wsrest_veiculo = "localhost:8080"
#    url_wsrest_veiculo = "192.168.1.107:8080"
#    url_wsrest_veiculo = "192.168.20.101:8080"
#    url_wsrest_veiculo = "192.168.0.101:8080"

    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):

        tg = int(time.time() * 1000)
        web.header('Content-Type', 'application/xml')
        global recurso
# ToDo: Nao aceitar chamada com parametro.
#        if not name:
#            name = 'World.'
        tg = int(time.time() * 1000) - tg
        web.debug('GET total time: ' + str(tg) + " ms")
        return self.to_xml(recurso)

    def POST(self, name):

        tg = int(time.time() * 1000)
        global recurso
#        web.debug("POST...start fuzzy follow")
        # Sinalizador. Permite apenas uma transferencia em andamento por vez.
        if recurso['status'] == 'ready':
#            web.debug("POST...start")
            self.calculate_and_move()
#            web.debug("POST...end")
            #self.to_device()
            #self.tts.synth('Post')
            status_returned = recurso['status']
        else:
            status_returned = 'busy'

        tg = int(time.time() * 1000) - tg
        web.debug('POST total time: ' + str(tg) + " ms")

        recurso['status'] = 'ready'
        #recurso['texto'] = ''
        return '<status>' + status_returned + '</status>'

    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
#        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  "FuzzyFollow")

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % "FuzzyFollow")
        stream.seek(0)
        return stream.read()

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
                    if key != 'status' and key != 'id':
                        stringXml = xml[inicio + len(key) + 2 : final]
                        if len(stringXml) > 0: # Ignorando chaves vazias.
                            # Diferenciando valor (string ou int)
                            if isinstance(recurso[key], str):
                                recurso[key] = stringXml
                            else:
                                recurso[key] = int(stringXml)
        #print recurso



    # Retorna as pertinencias da medida x aos conjuntos fuzzy
    # definidos para a variavel linguistica POSICAO DO LANDMARK NA TELA.
    # Os valores de x estao na faixa de 0 a 100%,
    # sendo 50%, ou no meio da tela, o valor ideal.
    # O percentual x eh calculado dividindo o x0 da posicao
    # pela largura xt da tela, ou seja: (x=x0/xt)
    # Funcoes de pertinencia TRIANGULARES/TRAPEZOIDAS
    def posicao_x(self, x):
        # Pontos dos triangulos ou trapezios dos conjuntos fuzzy.
        t_l = ((0.,30.,\
            20.,30.,38.,\
            30.,38.,47.,\
            45.,50.,55.,\
            53.,62.,70.,\
            62.,70.,80.,\
            70.,100.))
        mi = []

        # Conjunto ME - Muito a Esquerda
        larg0 = abs(t_l[0]-t_l[1])
        if x>=t_l[0] and x<=t_l[1]:
           mi.append(abs((1/larg0)*(x-t_l[1])))
        else:
           mi.append(0.)

        # Conjunto ES - Esquerda
        larg0 = abs(t_l[2]-t_l[3])
        larg1 = abs(t_l[3]-t_l[4])
        if x<=t_l[2]:
           mi.append(0.)
        elif x>t_l[2] and x<=t_l[3]:
           mi.append((1/larg0)*(x-t_l[2]))
        elif x>t_l[3] and x<t_l[4]:
           mi.append(abs((1/larg1)*(x-t_l[4])))
        else:
           mi.append(0.)

        # Conjunto EC - Esquerda Centro
        larg0 = abs(t_l[5]-t_l[6])
        larg1 = abs(t_l[6]-t_l[7])
        if x<=t_l[5]:
           mi.append(0.)
        elif x>t_l[5] and x<=t_l[6]:
           mi.append((1/larg0)*(x-t_l[5]))
        elif x>t_l[6] and x<t_l[7]:
           mi.append(abs((1/larg1)*(x-t_l[7])))
        else:
           mi.append(0.)

        # Conjunto CE - Centro
        larg0 = abs(t_l[8]-t_l[9])
        larg1 = abs(t_l[9]-t_l[10])
        if x<=t_l[8]:
           mi.append(0.)
        elif x>t_l[8] and x<=t_l[9]:
           mi.append((1/larg0)*(x-t_l[8]))
        elif x>t_l[9] and x<t_l[10]:
           mi.append(abs((1/larg1)*(x-t_l[10])))
        else:
           mi.append(0.)

        # Conjunto DC - Direita Centro
        larg0 = abs(t_l[11]-t_l[12])
        larg1 = abs(t_l[12]-t_l[13])
        if x<=t_l[11]:
           mi.append(0.)
        elif x>t_l[11] and x<=t_l[12]:
           mi.append((1/larg0)*(x-t_l[11]))
        elif x>t_l[12] and x<t_l[13]:
           mi.append(abs((1/larg1)*(x-t_l[13])))
        else:
           mi.append(0.)

        # Conjunto DI - Direita
        larg0 = abs(t_l[14]-t_l[15])
        larg1 = abs(t_l[15]-t_l[16])
        if x<=t_l[14]:
           mi.append(0.)
        elif x>t_l[14] and x<=t_l[15]:
           mi.append((1/larg0)*(x-t_l[14]))
        elif x>t_l[15] and x<t_l[16]:
           mi.append(abs((1/larg1)*(x-t_l[16])))
        else:
           mi.append(0.)

        # Conjunto MD - Muito a Direita
        larg0 = abs(t_l[17]-t_l[18])
        if x>t_l[17] and x<=t_l[18]:
           mi.append((1/larg0)*(x-t_l[17]))
        else:
           mi.append(0.)

        return mi[:]

    # Retorna as pertinencias da medida x0 aos conjuntos fuzzy
    # definidos para a variavel linguistica DISTANCIA Z DO LANDMARK.
    # Funcoes de pertinencia TRIANGULARES/TRAPEZOIDAS
    def posicao_z(self, x):
        # Pontos dos triangulos ou trapezios dos conjuntos fuzzy.
        p_l = ((0.,750.,\
            600.,860.,915.,\
            860.,945.))

        mi = []

        # Conjunto Perto (PE)
        larg0 = abs(p_l[0]-p_l[1])
        if x <= p_l[0]:
           mi.append(1.)
        elif x > p_l[0] and x < p_l[1]:
           mi.append(abs((1/larg0)*(x-p_l[1])))
        else:
           mi.append(0.)

        # Conjunto Medio (ME)
        larg0 = abs(p_l[2]-p_l[3])
        larg1 = abs(p_l[3]-p_l[4])
        if x <= p_l[2]:
           mi.append( 0.)
        elif x > p_l[2] and x <= p_l[3]:
           mi.append( (1/larg0)*(x-p_l[2]))
        elif x > p_l[3] and x < p_l[4]:
           mi.append( abs((1/larg1)*(x-p_l[4])))
        else:
           mi.append( 0.)

        # Conjunto Longe (LO)
        larg0 = abs(p_l[5]-p_l[6])
        if x >= p_l[6]:
           mi.append( 1.)
        elif x >= p_l[5] and x < p_l[6]:
           mi.append( (1/larg0)*(x-p_l[5]))
        else:
           mi.append( 0.)

        return mi[:]


    # Retorna as pertinencias da medida x aos conjuntos fuzzy
    # definidos para a variavel linguistica ANGULO THETA.
    # Funcoes de pertinencia TRIANGULARES/TRAPEZOIDAS
    def theta(self, x):
        # Pontos dos triangulos ou trapezios dos conjuntos fuzzy.
        t_l = ((-45.,-13.,\
            -20.,-13.,-6.,\
            -12.,-6.,-0.,\
            -2.,0.,2.,\
            0.,6.,12.,\
            6.,13.,20.,\
            13.,45.))

        mi = []

        # Conjunto NB Neg Big
        larg0 = abs(t_l[0]-t_l[1])
        if x>=t_l[0] and x<=t_l[1]:
           mi.append(abs((1/larg0)*(x-t_l[1])))
        else:
           mi.append(0.)

        # Conjunto NM Neg Med
        larg0 = abs(t_l[2]-t_l[3])
        larg1 = abs(t_l[3]-t_l[4])
        if x<=t_l[2]:
           mi.append(0.)
        elif x>t_l[2] and x<=t_l[3]:
           mi.append((1/larg0)*(x-t_l[2]))
        elif x>t_l[3] and x<t_l[4]:
           mi.append(abs((1/larg1)*(x-t_l[4])))
        else:
           mi.append(0.)

        # Conjunto NS Neg Small
        larg0 = abs(t_l[5]-t_l[6])
        larg1 = abs(t_l[6]-t_l[7])
        if x<=t_l[5]:
           mi.append(0.)
        elif x>t_l[5] and x<=t_l[6]:
           mi.append((1/larg0)*(x-t_l[5]))
        elif x>t_l[6] and x<t_l[7]:
           mi.append(abs((1/larg1)*(x-t_l[7])))
        else:
           mi.append(0.)

        # Conjunto ZE Zero
        larg0 = abs(t_l[8]-t_l[9])
        larg1 = abs(t_l[9]-t_l[10])
        if x<=t_l[8]:
           mi.append(0.)
        elif x>t_l[8] and x<=t_l[9]:
           mi.append((1/larg0)*(x-t_l[8]))
        elif x>t_l[9] and x<t_l[10]:
           mi.append(abs((1/larg1)*(x-t_l[10])))
        else:
           mi.append(0.)

        # Conjunto PS Posit Small
        larg0 = abs(t_l[11]-t_l[12])
        larg1 = abs(t_l[12]-t_l[13])
        if x<=t_l[11]:
           mi.append(0.)
        elif x>t_l[11] and x<=t_l[12]:
           mi.append((1/larg0)*(x-t_l[11]))
        elif x>t_l[12] and x<t_l[13]:
           mi.append(abs((1/larg1)*(x-t_l[13])))
        else:
           mi.append(0.)

        # Conjunto PM Posit Med
        larg0 = abs(t_l[14]-t_l[15])
        larg1 = abs(t_l[15]-t_l[16])
        if x<=t_l[14]:
           mi.append(0.)
        elif x>t_l[14] and x<=t_l[15]:
           mi.append((1/larg0)*(x-t_l[14]))
        elif x>t_l[15] and x<t_l[16]:
           mi.append(abs((1/larg1)*(x-t_l[16])))
        else:
           mi.append(0.)

        # Conjunto PB Posit Big
        larg0 = abs(t_l[17]-t_l[18])
        if x>t_l[17] and x<=t_l[18]:
           mi.append((1/larg0)*(x-t_l[17]))
        else:
           mi.append(0.)


        return mi[:]




    # Exemplo simples de base de regras nebulosas
    #
    # ENTRADA
    #     mi1: graus de pertinencia da variavel x1 (posicao x, em %)
    #     mi2: graus de pertinencia da variavel x2 (posicao z)
    #     mi_out: funcoes de pertinencia da variavel de saida y (angulo teta, graus)
    # SAIDA
    #     rule_out: Conjuntos fuzzy de saida modificados para todas as regras
    def regras_xz(self, mi1, mi2, mi_out):

        size_mi_out = mi_out.shape

        # Matriz de regras fuzzy.
        rf = numpy.array(((0, 1, 2, 3, 4, 5, 6),\
            (0, 1, 2, 3, 4, 5, 6),\
            (1, 1, 2, 3, 4, 5, 5)))

#        web.debug("rf shape = " + str(rf.shape))

        # loop das regras fuzzy.
        first = True
        for i in range(len(mi1)):
            for j in range(len(mi2)):
                min_temp = min(mi1[i], mi2[j])

                mi_out_temp = numpy.minimum(min_temp, mi_out[:, rf[j,i]])\
                    .reshape(size_mi_out[0],1)

                # montando matriz(vetor) retorno.
                if (first):
                    rule_out = numpy.transpose(mi_out_temp)
                    first = False;
                else:
                    rule_out = numpy.vstack((rule_out, numpy.transpose(mi_out_temp)))
#                web.debug("rule_out shape = " + str(rule_out.shape))

        return rule_out.copy()


    # ENTRADA
    #     mi1: graus de pertinencia da variavel x1 (angulo theta, em graus)
    #     mi2: graus de pertinencia da variavel x2 (posicao z)
    #     mi_out: funcoes de pertinencia da variavel de saida y (distancia, em ms)
    # SAIDA
    #     rule_out: Conjuntos fuzzy de saida modificados para todas as regras
    def regras_tz(self, mi1, mi2, mi_out):

        size_mi_out = mi_out.shape

        # Matriz de regras fuzzy.
        rf = numpy.array(((0, 1, 1, 2, 1, 1, 0),\
            (0, 1, 2, 3, 2, 1, 0),\
            (0, 1, 2, 3, 2, 1, 0)))

        # loop das regras fuzzy.
        first = True
        for i in range(len(mi1)):
            for j in range(len(mi2)):
                min_temp = min(mi1[i], mi2[j])
                mi_out_temp = numpy.minimum(min_temp, mi_out[:, rf[j,i]])\
                    .reshape(size_mi_out[0],1)
                # montando matriz(vetor) retorno.
                if (first):
                    rule_out = numpy.transpose(mi_out_temp)
                    first = False;
                else:
                    rule_out = numpy.vstack((rule_out, numpy.transpose(mi_out_temp)))

        return rule_out.copy()


    def calculate_and_move(self):
        # Implementacao de um sistema de inferencia fuzzy
        #% PRIMEIRAS ENTRADAS: x1 (posicao horizontal relativa x, %), x2 (distancia z)
        #% PRIMEIRA SAIDA:  y (angulo teta, graus)
        #% SEGUNDAS ENTRADAS: x1 (angulo teta, graus), x2 (posicao z)
        #% SEGUNDA SAIDA:  y (distancia a percorrer,  ms)

        # Lendo parametros.
        global recurso
        # Lendo dados recebidos (exceto status e id)
        self.from_xml(web.data())
        recurso['status'] = 'sending to device'
        # Trajetoria x (X1, %), posicao z (X2) em cada passo.
        X1=[recurso["relative horizontal position"]]
        X2=[recurso["distance"]]

        # ToDo:
        # Validando parametros recebidos

        # PRIMEIRA VARIAVEL DE SAIDA (Funcoes de Pertinencia)
        y = numpy.arange(-45,45,0.1)  # Universo de discurso da variavel de saida

        first_e = True
        for i in numpy.arange(len(y)):
            aux = self.theta(y[i]);
            if first_e == True:
                first_e = False
                mi_out = aux
            else:
                mi_out = numpy.vstack((mi_out, aux))

        # SEGUNDA VARIAVEL DE SAIDA (Funcoes de Pertinencia)
        y2 = numpy.arange(0,2000,1)  # Universo de discurso da variavel de saida

        first_e = True
        for i in numpy.arange(len(y2)):
            aux = self.distancia_ms(y2[i]);
            if first_e == True:
                first_e = False
                mi_out2 = aux
            else:
                mi_out2 = numpy.vstack((mi_out2, aux))




        #%%%%%%%%%%%
        # ETAPA 1: FUZZIFICACAO
        #%%%%%%%%%%%%

        mi1 = self.posicao_x(X1[0])   # Pertinencias para variavel POSICAO X
        mi2 = self.posicao_z(X2[0])  	   # Pertinencias para variavel ANGULO FI

#        web.debug("posicao x ======: " + str(mi1))
#        web.debug("posicao z ======: " + str(mi2))

        #%%%%%%%%%%%
        # ETAPA 2: AVALIACAO DAS REGRAS FUZZY
        #%%%%%%%%%%%

        rule_out = self.regras_xz(mi1[:],mi2[:],mi_out);  # Conjuntos fuzzy de saida de todas as regras

        #%%%%%%%%%%%
        # ETAPA 3: INFERENCIA FUZZY (AGREGACAO - OR)
        #%%%%%%%%%%%%

        F_OUT=sum(rule_out);

        #%%%%%%%%%%%
        # ETAPA 4: DESFUZZIFICACAO (CENTRO DE GRAVIDADE)
        #%%%%%%%%%%%%

        Y = sum(F_OUT * y)/sum(F_OUT)
#        web.debug("Y = " + str(Y))

        if math.isnan(Y) == True:
            Y = 0

        # - converte saida (Y) em comando para enviar ao wsrest_veiculo.
        saida_ms = self.graus_2_millisec(Y) # convertendo graus em milissegundos

#        web.debug("e saida_ms = " + str(saida_ms))


        ##############################################
        #  DETERMINACAO DA SEGUNDA VARIAVEL DE SAIDA
        ##############################################

        #%%%%%%%%%%%
        # ETAPA 1: FUZZIFICACAO
        #%%%%%%%%%%%%

        mi1 = self.theta(Y)   # Pertinencias para variavel THETA X
        mi2 = self.posicao_z(X2[0])  	   # Pertinencias para variavel DISTANCIA Z

#        web.debug("angulo theta ======: " + str(mi1))
#            web.debug("posicao z ======: " + str(mi2))

        #%%%%%%%%%%%
        # ETAPA 2: AVALIACAO DAS REGRAS FUZZY
        #%%%%%%%%%%%

        rule_out2 = self.regras_tz(mi1[:],mi2[:],mi_out2);  # Conjuntos fuzzy de saida de todas as regras

        #%%%%%%%%%%%
        # ETAPA 3: INFERENCIA FUZZY (AGREGACAO - OR)
        #%%%%%%%%%%%%

        F_OUT2=sum(rule_out2);

        #%%%%%%%%%%%
        # ETAPA 4: DESFUZZIFICACAO (CENTRO DE GRAVIDADE)
        #%%%%%%%%%%%%

        Y2 = sum(F_OUT2 * y2)/sum(F_OUT2)
#        web.debug("Y2 = " + str(Y2))

        if math.isnan(Y2) == True:
            Y2 = 0


        #########################################
        # INICIANDO OS MOVIMENTOS (GIRO E AVANCO)
        #########################################

        # girando e avancado.
        self.to_veiculo(saida_ms, int(Y2))

        recurso['status'] = 'post ok'
        return"fuzzy follow ok"


    def to_veiculo(self, saida_giro, saida_distancia):
        # Comando girar.
#        direcao_rotacao = 4 if self.leitura[3]>0 else 6 if self.leitura[3]<0 else 0

        if saida_giro != 0:
            direcao_rotacao = 9 if saida_giro>0 else 7
            # Preparando comando girar com velocidade minima.
            recursoXml = "<VeiculoRO> \
                <id_timeout>1</id_timeout> \
                <direcao>" + str(direcao_rotacao) + "</direcao> \
                <tempo>" + str(abs(saida_giro)) + "</tempo> \
                <velocidade>80</velocidade> \
                </VeiculoRO>"
            # Enviar comando.
            conn = httplib.HTTPConnection(self.url_wsrest_veiculo)
            conn.request("POST", "/", recursoXml)
            response = conn.getresponse()
            conn.close()
#            web.debug("girar = " + str(direcao_rotacao) + "  " + str(saida_giro)) # + "  " + recursoXml)

        if saida_distancia > 100:
            # Preparando comando avancar com velocidade minima.
            recursoXml = "<VeiculoRO> \
                <id_timeout>1</id_timeout> \
                <direcao>2</direcao> \
                <tempo>" + str(saida_distancia) + "</tempo> \
                <velocidade>80</velocidade> \
                </VeiculoRO>"
#            web.debug("avancar " + recursoXml)
            # Enviar comando.
            conn = httplib.HTTPConnection(self.url_wsrest_veiculo)
            conn.request("POST", "/", recursoXml)
            response = conn.getresponse()
            conn.close()

        # Retorna ao loop fuzzy.


    def graus_2_millisec(self, angulo_saida):
        if abs(angulo_saida) < 1:
            tempo_giro = 0      # ignorando movimento menor q 1 grau.
        elif angulo_saida < 0:
            tempo_giro = 7500   # p/esquerda
        else:
            tempo_giro = 6000   # p/direita

        return int((angulo_saida/360)*tempo_giro)

#    def rad_2_graus(self, angulo_radianos):
#        return int((angulo_radianos/(2*numpy.pi))*360)

#    def __done__(self):



    # Retorna as pertinencias da medida x0 aos conjuntos fuzzy
    # definidos para a variavel linguistica DISTANCIA A PERCORRER.
    # Funcoes de pertinencia TRIANGULARES/TRAPEZOIDAS
    def distancia_ms(self, x):
        # Pontos dos triangulos ou trapezios dos conjuntos fuzzy.
        p_l = ((0.,100.,\
            100.,350.,600.,\
            350.,850.,1350.,\
            850.,2000.))

        mi = []

        # Conjunto Sem Movimento (SM)
        larg0 = abs(p_l[0]-p_l[1])
        if x <= p_l[0]:
           mi.append(1.)
        elif x > p_l[0] and x < p_l[1]:
           mi.append(abs((1/larg0)*(x-p_l[1])))
        else:
           mi.append(0.)

        # Conjunto Distancia Curta (DC)
        larg0 = abs(p_l[2]-p_l[3])
        larg1 = abs(p_l[3]-p_l[4])
        if x <= p_l[2]:
           mi.append( 0.)
        elif x > p_l[2] and x <= p_l[3]:
           mi.append( (1/larg0)*(x-p_l[2]))
        elif x > p_l[3] and x < p_l[4]:
           mi.append( abs((1/larg1)*(x-p_l[4])))
        else:
           mi.append( 0.)

        # Conjunto Distancia Media (DM)
        larg0 = abs(p_l[5]-p_l[6])
        larg1 = abs(p_l[6]-p_l[7])
        if x <= p_l[5]:
           mi.append( 0.)
        elif x > p_l[5] and x <= p_l[6]:
           mi.append( (1/larg0)*(x-p_l[5]))
        elif x > p_l[6] and x < p_l[7]:
           mi.append( abs((1/larg1)*(x-p_l[7])))
        else:
           mi.append( 0.)

        # Conjunto Distancia Grande (DG)
        larg0 = abs(p_l[8]-p_l[9])
        if x >= p_l[9]:
           mi.append( 1.)
        elif x >= p_l[8] and x < p_l[9]:
           mi.append( (1/larg0)*(x-p_l[8]))
        else:
           mi.append( 0.)

        return mi[:]


application = web.application(urls, globals())

if __name__ == "__main__":
    application.run()

#application = web.application(urls, globals()).wsgifunc()
