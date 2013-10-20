#! /usr/bin/python

__author__="marcus"
__date__ ="$Feb 6, 2011 2:49:51 PM$"


import web
import StringIO
import time
import numpy
from pylab import plot, show
from math import tan
import MySQLdb
import httplib



urls = (
        '/(.*)', 'index'
        )

web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

recurso = { \
    "status" : "ready", \
    "landmark" : "", \
    "id" : 0 \
    }

# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
    #, initializer={'logged_in': False})

class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # Conectando com o BD.
    db = MySQLdb.connect(
        host="192.168.1.102", port=3306, user="robot", passwd="123456", db="robot")

    leitura = numpy.array((0.0, 0.0, 0.0, 0.0)) # x,y,z e fi calculado.
    id_leitura_ant = 0
    final = 0
    fi_ant = 0

    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):

        web.header('Content-Type', 'application/xml')
        global recurso
        #self.tts.synth('Get')
        # ToDo: Nao aceitar chamada com parametro.
#        if not name:
#            name = 'World.'
        return self.to_xml(recurso)

    def POST(self, name):

        global recurso
        # Sinalizador. Permite apenas uma transferencia em andamento por vez.
        if recurso['status'] == 'ready':
            web.debug("POST...start")
            self.estacionar()
            web.debug("POST...end")
            #self.to_device()
            #self.tts.synth('Post')
            status_returned = recurso['status']
        else:
            status_returned = 'busy'

        recurso['status'] = 'ready'
        #recurso['texto'] = ''
        return '<status>' + status_returned + '</status>'

    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
#        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  "TtsRO")

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % "TtsRO")
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
                    if key != 'status' and key != 'id': # Ignorando atributo 'status'.
                        stringXml = xml[inicio + len(key) + 2 : final]
                        if len(stringXml) > 0: # Ignorando chaves vazias.
                            # Diferenciando valor (string ou int)
                            if isinstance(recurso[key], str):
                                recurso[key] = stringXml
                            else:
                                recurso[key] = int(stringXml)
        #print recurso



    # Retorna as pertinencias da medida x aos conjuntos fuzzy
    # definidos para a variavel linguistica POSICAO.
    #
    # Funcoes de pertinencia TRIANGULARES/TRAPEZOIDAS
    def posicao(self, x):
        # Pontos dos triangulos ou trapezios dos conjuntos fuzzy.
        p_l = ((-40.,-15.,\
            -20.,-10.,0.,\
            -5.,0.,5.,\
            0.,10.,20.,\
            15.,40.))
        mi = []

        # Conjunto LE
        larg0 = abs(p_l[0]-p_l[1])
        if x <= p_l[0]:
           mi.append(1.)
        elif x > p_l[0] and x < p_l[1]:
           mi.append(abs((1/larg0)*(x-p_l[1])))
        else:
           mi.append(0.)

        # Conjunto LC Left Center
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

        # Conjunto CE Center
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

        # Conjunto RC Right Center
        larg0 = abs(p_l[8]-p_l[9])
        larg1 = abs(p_l[9]-p_l[10])
        if x <= p_l[8]:
           mi.append( 0.)
        elif x > p_l[8] and x <= p_l[9]:
           mi.append( (1/larg0)*(x-p_l[8]))
        elif x > p_l[9] and x < p_l[10]:
           mi.append( abs((1/larg1)*(x-p_l[10])))
        else:
           mi.append( 0.)

        # Conjunto RC Right
        larg0 = abs(p_l[11]-p_l[12])
        if x >= p_l[12]:
           mi.append( 1.)
        elif x >= p_l[11] and x <= p_l[12]:
           mi.append( (1/larg0)*(x-p_l[11]))
        else:
           mi.append( 0.)

        return mi[:]

    # Retorna as pertinencias da medida x aos conjuntos fuzzy
    # definidos para a variavel linguistica ANGULO FI.
    # Funcoes de pertinencia TRIANGULARES/TRAPEZOIDAS
    def fi(self, x):
        # Pontos dos triangulos ou trapezios dos conjuntos fuzzy.
        f_l = ((-90.,-67.,-42.,\
            -47.,-30.,-15.,\
            -30.,-15.,0.,\
            -5.,0.,5.,\
            0.,15.,30.,\
            15.,30.,47.,\
            42.,67.,90.))
        mi = []

        # Conjunto RB Right Below
        larg0 = abs(f_l[0]-f_l[1])
        larg1 = abs(f_l[1]-f_l[2])
        if x <= f_l[0]:
           mi.append( 0.)
        elif x > f_l[0] and x <= f_l[1]:
           mi.append( (1/larg0)*(x-f_l[0]))
        elif x > f_l[1] and x < f_l[2]:
           mi.append( abs((1/larg1)*(x-f_l[2])))
        else:
           mi.append( 0.)

        # Conjunto RU Right Upper
        larg0 = abs(f_l[3]-f_l[4])
        larg1 = abs(f_l[4]-f_l[5])
        if x <= f_l[3]:
           mi.append( 0.)
        elif x > f_l[3] and x <= f_l[4]:
           mi.append((1/larg0)*(x-f_l[3]))
        elif x > f_l[4] and x < f_l[5]:
           mi.append(abs((1/larg1)*(x-f_l[5])))
        else:
           mi.append(0.)

        # Conjunto RV Right Vert
        larg0 = abs(f_l[6]-f_l[7])
        larg1 = abs(f_l[7]-f_l[8])
        if x<=f_l[6]:
           mi.append(0.)
        elif x>f_l[6] and x<=f_l[7]:
           mi.append((1/larg0)*(x-f_l[6]))
        elif x>f_l[7] and x<f_l[8]:
           mi.append(abs((1/larg1)*(x-f_l[8])))
        else:
           mi.append(0.)


        # Conjunto VE Vert
        larg0 = abs(f_l[9]-f_l[10])
        larg1 = abs(f_l[10]-f_l[11])
        if x <= f_l[9]:
           mi.append(0.)
        elif x>f_l[9] and x<=f_l[10]:
           mi.append((1/larg0)*(x-f_l[9]))
        elif x>f_l[10] and x<f_l[11]:
           mi.append(abs((1/larg1)*(x-f_l[11])))
        else:
           mi.append(0.)


        # Conjunto LV Left Vert
        larg0 = abs(f_l[12]-f_l[13])
        larg1 = abs(f_l[13]-f_l[14])
        if x<=f_l[12]:
           mi.append(0.)
        elif x>f_l[12] and x<=f_l[13]:
           mi.append((1/larg0)*(x-f_l[12]))
        elif x>f_l[13] and x<f_l[14]:
           mi.append(abs((1/larg1)*(x-f_l[14])))
        else:
           mi.append(0.)


        # Conjunto LU Left Upper
        larg0 = abs(f_l[15]-f_l[16])
        larg1 = abs(f_l[16]-f_l[17])
        if x<=f_l[15]:
           mi.append(0.)
        elif x>f_l[15] and x<=f_l[16]:
           mi.append((1/larg0)*(x-f_l[15]))
        elif x>f_l[16] and x<f_l[17]:
           mi.append(abs((1/larg1)*(x-f_l[17])))
        else:
           mi.append(0.)

        # Conjunto LB Left Below
        larg0 = abs(f_l[18]-f_l[19])
        larg1 = abs(f_l[19]-f_l[20])
        if x<=f_l[18]:
           mi.append(0.)
        elif x>f_l[18] and x<=f_l[19]:
           mi.append((1/larg0)*(x-f_l[18]))
        elif x>f_l[19] and x<f_l[20]:
           mi.append(abs((1/larg1)*(x-f_l[20])))
        else:
           mi.append(0.)

        return mi[:]

    # Retorna as pertinencias da medida x aos conjuntos fuzzy
    # definidos para a variavel linguistica ANGULO THETA.
    # Funcoes de pertinencia TRIANGULARES/TRAPEZOIDAS
    def theta(self, x):
        # Pontos dos triangulos ou trapezios dos conjuntos fuzzy.
#        t_l = ((-15.,-8.,\
#            -12.,-8.,-2.5,\
#            -6.,-3.,0.,\
#            -2.5,0.,2.5,\
#            0.,3.,6.,\
#            2.5,8.,12.,\
#            8.,15.))

        t_l = ((-10.,-6.,\
            -8.,-6.,-2.,\
            -4.,-2.,0.,\
            -2,0.,2,\
            0.,2.,4.,\
            2.,6.,8.,\
            6.,10.))
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
    #     mi1: graus de pertinencia da variavel x1 (posicao x)
    #     mi2: graus de pertinencia da variavel x2 (angulo fi, graus)
    #     mi_out: funcoes de pertinencia da variavel de saida y (angulo teta, graus)
    # SAIDA
    #     rule_out: Conjuntos fuzzy de saida modificados para todas as regras
    def regras(self, mi1, mi2, mi_out):

#        rule_out = numpy.empty((35,1))
        size_mi_out = mi_out.shape
#        rule_out = numpy.empty((1, size_mi_out[0]))
#        web.debug("mi_out shape = " + str(size_mi_out))
#        web.debug("mi1 shape = " + str(mi1.shape))
#        web.debug("mi2 shape = " + str(mi2.shape))

        # Matriz de regras fuzzy.
        rf = numpy.array(((6, 5, 4, 3, 3),\
            (5, 4, 4, 3, 3),\
            (4, 4, 3, 3, 3),\
            (4, 3, 3, 3, 2),\
            (3, 3, 3, 2, 2),\
            (3, 3, 2, 2, 1),\
            (3, 3, 2, 1, 0)))

#        web.debug("rf shape = " + str(rf.shape))

        # loop das regras fuzzy.
        first = True
        for i in range(len(mi1)):
            for j in range(len(mi2)):
#                web.debug("i,j = " + str(i) + "  " + str(j) + "  " + str(len_mi1[1]) + "  " + str(len_mi2[1]))
#                web.debug("mi1(i),mi2(j) size = " + str(mi1(i)) + "  " + str(mi2(j)))
                min_temp = min(mi1[i], mi2[j])
#                web.debug("min values = " + str(mi1[0,i]) + " " + str(mi2[0,j]))
                # usando matriz de regras.
#                web.debug("min_temp value = " + str(min_temp))
#                web.debug("mi_out shape = " + str(mi_out.shape))
#                web.debug("rf[j,i] = " + str(rf[j,i]))
#                ind_rf = rf[j,i]
                mi_out_temp = numpy.minimum(min_temp, mi_out[:, rf[j,i]])\
                    .reshape(size_mi_out[0],1)

#                web.debug("mi_out_temp shape = " + str(mi_out_temp.shape))
                # montando matriz(vetor) retorno.
                if (first):
                    rule_out = numpy.transpose(mi_out_temp)
                    first = False;
                else:
                    rule_out = numpy.vstack((rule_out, numpy.transpose(mi_out_temp)))
#                web.debug("rule_out shape = " + str(rule_out.shape))

        return rule_out.copy()


    def estacionar(self):
        # Implementacao de um sistema de inferencia fuzzy
        #% ENTRADAS: x1 (posicao x), x2 (angulo fi, graus)
        #% SAIDA:  y (angulo teta, graus)

        # Valores iniciais aleatorios para x1 e x2.
#        x1=round(numpy.random.rand(1)*100)
#        x2=round(numpy.random.rand(1)*360)-90 # graus

        # Primeiras leituras da posicao
        self.ler_xyz()
        while self.ler_xyz() == False:
            time.sleep(0.200)

        # Trajetoria (X1), angulos fi (X2 graus) e saida (X3 ms) em cada passo.
        X1=[self.leitura[0]]
        X2=[self.leitura[3]]
        X3=[0.]
        Out=[0]

        # VARIAVEL DE SAIDA (Funcoes de Pertinencia)
        y = numpy.arange(-10,10,0.05)  # Universo de discurso da variavel de saida

        first_e = True
        for i in numpy.arange(len(y)):
            aux = self.theta(y[i]);
#            web.debug("aux shape = " + str(aux.shape))
#            web.debug("mi_out shape = " + str(mi_out.shape))
            if first_e == True:
                first_e = False
                mi_out = aux
            else:
                mi_out = numpy.vstack((mi_out, aux))

        # Loop de n passos.
        for l in range(50):

            #%%%%%%%%%%%
            # ETAPA 1: FUZZIFICACAO
            #%%%%%%%%%%%%

            mi1 = self.posicao(X1[l])   # Pertinencias para variavel POSICAO X
            mi2 = self.fi(X2[l])  	   # Pertinencias para variavel ANGULO FI

            web.debug("posicao======: " + str(mi1))
            web.debug("fi===========: " + str(mi2))

#            if l == 4:
#                web.debug("posicao = " + str(mi1))
#                web.debug("fi = " + str(mi2))
            #%%%%%%%%%%%
            # ETAPA 2: AVALIACAO DAS REGRAS FUZZY
            #%%%%%%%%%%%

            rule_out = self.regras(mi1[:],mi2[:],mi_out);  # Conjuntos fuzzy de saida de todas as regras

            #%%%%%%%%%%%
            # ETAPA 3: INFERENCIA FUZZY (AGREGACAO - OR)
            #%%%%%%%%%%%%

            F_OUT=sum(rule_out);

            #%%%%%%%%%%%
            # ETAPA 4: DESFUZZIFICACAO (CENTRO DE GRAVIDADE)
            #%%%%%%%%%%%%

            Y = sum(F_OUT * y)/sum(F_OUT)

#            Y=Y/4   # reduzindo angulo

            # ToDo:
            # - converter saida (Y) em comando para enviar ao wsrest_veiculo.
            saida_ms = self.graus_2_millisec(Y) # convertendo graus em milissegundos

            web.debug("Y e saida_ms = " + str(Y) + "   " + str(saida_ms))

            # deve considerar rotacao anterior.
            if saida_ms != 0:
                saida_dif = int(saida_ms - X3[l])
            else:
                saida_dif = saida_ms
            X3 = numpy.vstack((X3,saida_dif))

            web.debug("saida considerada = " + str(saida_dif))

            # girando (saida<>0) ou avancando (saida=0)
            self.to_veiculo(saida_dif)
            if saida_dif != 0:
                # Avancando porque o comando acima foi de rotacao.
                self.to_veiculo(0)

            # atualizando posicao, desconsidera variacao angular maior q N graus.
#            time.sleep(0.300) # Aguarda um tempo para ler a nova
                              # posicao, porque o driver grava +-5 leituras p/seg.
            z_ant = self.leitura[2]
            while self.ler_xyz() == False \
                or abs(X2[l]-self.leitura[3]) > 15:
                time.sleep(0.100)


            # Calculando angulo para manter o marcador no campo de visao.
#            denominador = X1[l]-self.leitura[0]
#            if denominador != 0:
#                beta_ant = numpy.arctan(\
#                    tan(abs((z_ant-self.leitura[2])/denominador)))
#                beta_ant = self.rad_2_graus(beta_ant)
#                delta = ((90 - self.leitura[3]) - beta_ant)*(-1)
#                if abs(delta) > abs(saida_ms):
#                    delta = saida_ms * (-1)
#
#                web.debug('beta_ant = ' + str(beta_ant))
#                web.debug('alpha_1 = ' + str((90 - self.leitura[3])))
#                # Girando para ajustar postura
#                self.to_veiculo(self.graus_2_millisec(delta))

            x3 = self.leitura[0]

            #x4=X2(l)-Y;
            x4 = self.leitura[3]
#            x4=90-Y;	# considerando que a inclinacao da roda eh em relacao
            #%if x4<-90,
            #%	x4=-90;
            #%elseif x4>270,
            #%	x4=270;

            X1 = numpy.vstack((X1,x3))
            # atualizando angulo
            X2 = numpy.vstack((X2,x4))
            Out = numpy.vstack((Out,Y))

            if self.leitura[2] < 60:
                self.final = self.final + 1
                if self.final > 3:
                    break
            else:
                self.final = 0

        plot(X1)
        plot(X2)
        plot(Out)
        show()

        return"fuzzy ok"

    def to_veiculo(self, saida):
        # Comando girar.
#        direcao_rotacao = 4 if self.leitura[3]>0 else 6 if self.leitura[3]<0 else 0
        
        if saida != 0:
            direcao_rotacao = 9 if saida>0 else 7
#            direcao_rotacao = 1 if saida>0 else 3
            # Preparando comando girar com velocidade minima.
            recursoXml = "<VeiculoRO> \
                <id_timeout>1</id_timeout> \
                <direcao>" + str(direcao_rotacao) + "</direcao> \
                <tempo>" + str(abs(saida)) + "</tempo> \
                <velocidade>80</velocidade> \
                </VeiculoRO>"
#                <tempo>200</tempo> \
            web.debug("girar = " + str(direcao_rotacao) + "  " + str(saida) + "  " + recursoXml)

        else:
            # Preparando comando avancar com velocidade minima.
            recursoXml = "<VeiculoRO> \
                <id_timeout>1</id_timeout> \
                <direcao>2</direcao> \
                <tempo>500</tempo> \
                <velocidade>80</velocidade> \
                </VeiculoRO>"
            web.debug("avancar " + recursoXml)

        # Enviar comando.
        conn = httplib.HTTPConnection("192.168.1.102:8080")
        conn.request("POST", "/", recursoXml)
        response = conn.getresponse()
        conn.close()

#        # Procurando manter o marcador no campo de visao.
#        if int(saida) != 0:
#            # Preparando comando girar com velocidade minima.
#            #tempo = (saida*1.1) if direcao_rotacao == 4 else (saida*0.9)
#            tempo = int(saida - saida_ant)
#            if tempo != 0:
#                direcao_rotacao = 6 if tempo >0 else 4 if tempo<0 else 0
#                recursoXml = "<VeiculoRO> \
#                    <id_timeout>1</id_timeout> \
#                    <direcao>" + str(direcao_rotacao) + "</direcao> \
#                    <tempo>" + str(abs(int(tempo))) + "</tempo> \
#                    <velocidade>80</velocidade> \
#                    </VeiculoRO>"
#                # Enviar comando girar.
#                conn = httplib.HTTPConnection("192.168.1.102:8080")
#                conn.request("POST", "/", recursoXml)
#                response = conn.getresponse()
#                conn.close()
#
#                web.debug("girar ao inverso")
#
#        saida_ant = saida

        # Retorna ao loop fuzzy.

    def ler_xyz(self):
        # Lendo ultima posicao gravada no BD.
        cursor = self.db.cursor()
        cursor.execute('''SELECT x, y, z, id FROM `tbl_landmark_position`''')
#            WHERE id = (select max(id) from tbl_landmark_position)''')
        leitura = ((0.0, 0.0, 0.0, 0))
        leitura = cursor.fetchone()
        # Fechando cursor.
        cursor.close()

#        web.debug("valores leitura direta = " + \
#            str(leitura[0]) + " , " + \
#            str(leitura[1]) + " , " + \
#            str(leitura[2]) + "   " + \
#            str(0 if leitura[2]==0 else leitura[0]/leitura[2]))

        if leitura[3] == self.id_leitura_ant:
            return False
        else:
            self.id_leitura_ant = leitura[3]

        self.leitura[0] = round(leitura[0] / 10)
        self.leitura[1] = round(leitura[1] / 10)
        self.leitura[2] = round(leitura[2] / 10)
        # Angulo em graus
        if round(leitura[2]) == 0:
            angulo = 0.
        else:
            angulo = tan(leitura[0]/leitura[2])
        angulo_radianos = numpy.arctan(angulo)
            
        self.leitura[3] = self.rad_2_graus(angulo_radianos)

        web.debug("===========================")
        web.debug("valores lidos = " + \
            str(self.leitura[0]) + " , " + \
            str(self.leitura[1]) + " , " + \
            str(self.leitura[2]) + " , " + \
            str(self.leitura[3]))
        web.debug("===========================")

        return True

    def graus_2_millisec(self, angulo_saida):
        if abs(angulo_saida) < 1:
            tempo_giro = 0      # ignorando movimento menor q 1 grau.
        elif angulo_saida < 0:        
            tempo_giro = 7500   # p/esquerda
        else:
            tempo_giro = 6000   # p/direita
        return int((angulo_saida/360)*tempo_giro)

    def rad_2_graus(self, angulo_radianos):
        return int((angulo_radianos/(2*numpy.pi))*360)

#    def __done__(self):



application = web.application(urls, globals())

if __name__ == "__main__":
    application.run()

#application = web.application(urls, globals()).wsgifunc()
