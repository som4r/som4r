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

        p = pylab.arange(0., 100., 0.5)
        P1=[]
        P2=[]
        P3=[]
        P4=[]
        P5=[]
        for x in p:
            t=self.posicao_x(x)
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

        pylab.savefig('/home/marcus/Desktop/posicaoX.png')
        #limpando a tela
        pylab.clf()



        p = pylab.arange(0., 3100., 1)
        P1=[]
        P2=[]
        P3=[]
        P4=[]
        P5=[]
        for x in p:
            t=self.posicao_z(x)
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

        pylab.savefig('/home/marcus/Desktop/posicaoZ.png')
        #limpando a tela
        pylab.clf()

        p = pylab.arange(-30., 30., 0.1)
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

    def posicao_x(self, x):
        # Pontos dos triangulos ou trapezios dos conjuntos fuzzy.
        p_l = ((10.,30.,\
            20.,30.,47.,\
            45.,50.,55.,\
            53.,70.,80.,\
            70.,90.))
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
        elif x >= p_l[11] and x < p_l[12]:
           mi.append( (1/larg0)*(x-p_l[11]))
        else:
           mi.append( 0.)

        return mi[:]



    def posicao_z(self, x):
        # Pontos dos triangulos ou trapezios dos conjuntos fuzzy.
        p_l = ((0.,600.,\
            400.,800.,1200.,\
            800.,1400.,1900.,\
            1400.,2000.,2600.,\
            2000.,3000.))
#        p_l = ((0.,250.,\
#            200.,400.,600.,\
#            550.,750.,950.,\
#            900.,1100.,1300.,\
#            1250.,1500.))
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
    # definidos para a variavel linguistica ANGULO THETA.
    # Funcoes de pertinencia TRIANGULARES/TRAPEZOIDAS
    def theta(self, x):
        # Pontos dos triangulos ou trapezios dos conjuntos fuzzy.
        t_l = ((-30.,-8.,\
            -12.,-8.,-4.,\
            -6.,-4.,-0.,\
            -2.,0.,2.,\
            0.,4.,6.,\
            4.,8.,12.,\
            8.,30.))

#        t_l = ((-30.,-15.,\
#            -25.,-15.,-5.,\
#            -12.,-6.,0.,\
#            -5.,0.,5.,\
#            0.,6.,12.,\
#            5.,15.,25.,\
#            15.,30.))

#        t_l = ((-15.,-8.,\
#            -12.,-8.,-2.5,\
#            -6.,-3.,0.,\
#            -2.5,0.,2.5,\
#            0.,3.,6.,\
#            2.5,8.,12.,\
#            8.,15.))

#        t_l = ((-10.,-6.,\
#            -8.,-6.,-2.,\
#            -4.,-2.,0.,\
#            -2,0.,2,\
#            0.,2.,4.,\
#            2.,6.,8.,\
#            6.,10.))
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



application = web.application(urls, globals())

if __name__ == "__main__":
    application.run()

#application = web.application(urls, globals()).wsgifunc()
