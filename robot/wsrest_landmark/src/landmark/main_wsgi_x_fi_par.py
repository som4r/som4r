#! /usr/bin/python

__author__="marcus"
__date__ ="$Feb 6, 2011 2:49:51 PM$"


import web
import numpy
from pylab import plot, show
import pylab

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


    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):

        web.header('Content-Type', 'application/xml')
        global recurso
        #self.tts.synth('Get')
        # ToDo: Nao aceitar chamada com parametro.
#        if not name:
#            name = 'World.'

        p = pylab.arange(-50., 50., 0.1)
        P1=[]
        P2=[]
        P3=[]
        P4=[]
        P5=[]
        for x in p:
            t=self.posicao(x)
            P1.append(t[0])
            P2.append(t[1])
            P3.append(t[2])
            P4.append(t[3])
            P5.append(t[4])
        plot(p,P1,'r-')
        plot(p,P2,'b-')
        plot(p,P3,'m-')
        plot(p,P4,'g-')
        plot(p,P5,'c-')

        pylab.savefig('/home/marcus/Desktop/posicao.png')
        #limpando a tela
        pylab.clf()



        p = pylab.arange(-90., 90., 0.1)
        P1=[]
        P2=[]
        P3=[]
        P4=[]
        P5=[]
        P6=[]
        P7=[]
        for x in p:
            t=self.fi(x)
            P1.append(t[0])
            P2.append(t[1])
            P3.append(t[2])
            P4.append(t[3])
            P5.append(t[4])
            P6.append(t[5])
            P7.append(t[6])
        plot(p,P1,'r-')
        plot(p,P2,'b-')
        plot(p,P3,'m-')
        plot(p,P4,'g-')
        plot(p,P5,'c-')
        plot(p,P6,'b-')
        plot(p,P7,'r-')

        pylab.savefig('/home/marcus/Desktop/fi.png')
        #limpando a tela
        pylab.clf()

        p = pylab.arange(-15., 15., 0.1)
        P1=[]
        P2=[]
        P3=[]
        P4=[]
        P5=[]
        P6=[]
        P7=[]
        for x in p:
            t=self.theta(x)
            P1.append(t[0])
            P2.append(t[1])
            P3.append(t[2])
            P4.append(t[3])
            P5.append(t[4])
            P6.append(t[5])
            P7.append(t[6])
        plot(p,P1,'r-')
        plot(p,P2,'b-')
        plot(p,P3,'m-')
        plot(p,P4,'g-')
        plot(p,P5,'c-')
        plot(p,P6,'b-')
        plot(p,P7,'r-')

        pylab.savefig('/home/marcus/Desktop/theta.png')

        show()

        return "ok"



    # Retorna as pertinencias da medida x aos conjuntos fuzzy
    # definidos para a variavel linguistica POSICAO.
    #
    # Funcoes de pertinencia TRIANGULARES/TRAPEZOIDAS
    def posicao(self, x):
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

        return mi

    # Retorna as pertinencias da medida x aos conjuntos fuzzy
    # definidos para a variavel linguistica ANGULO FI.
    # Funcoes de pertinencia TRIANGULARES/TRAPEZOIDAS
    def fi(self, x):
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

        return mi

    # Retorna as pertinencias da medida x aos conjuntos fuzzy
    # definidos para a variavel linguistica ANGULO THETA.
    # Funcoes de pertinencia TRIANGULARES/TRAPEZOIDAS
    def theta(self, x):
        t_l = ((-15.,-8.,\
            -12.,-8.,-2.5,\
            -6.,-3.,0.,\
            -2.5,0.,2.5,\
            0.,3.,6.,\
            2.5,8.,12.,\
            8.,15.))
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
        rf = numpy.array(((4, 5, 5, 6, 6),\
            (2, 4, 5, 6, 6),\
            (1, 2, 4, 5, 6),\
            (1, 1, 3, 5, 5),\
            (0, 1, 2, 4, 5),\
            (0, 0, 1, 2, 4),\
            (0, 0, 1, 1, 2)))

#        web.debug("rf shape = " + str(rf.shape))

        # loop das regras fuzzy.
        first = True
        len_mi1 = mi1.shape
        len_mi2 = mi2.shape
        for i in range(len_mi1[1]):
            for j in range(len_mi2[1]):
#                web.debug("i,j = " + str(i) + "  " + str(j) + "  " + str(len_mi1[1]) + "  " + str(len_mi2[1]))
#                web.debug("mi1(i),mi2(j) size = " + str(mi1(i)) + "  " + str(mi2(j)))
                min_temp = min(mi1[0,i], mi2[0,j])
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





application = web.application(urls, globals())

if __name__ == "__main__":
    application.run()

#application = web.application(urls, globals()).wsgifunc()
