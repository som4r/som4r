#! /usr/bin/python

__author__="marcus"
__date__ ="$Jul 3, 2011 10:41:47 PM$"


import web
import time
import freenect
import numpy
import math

import xml_util
import global_data
import http_util

import depth
import tilt
import depth_image
import rgb_image

urls = (
        '/tilt', tilt.app_tilt,
        '/depth', depth.app_depth,
        '/image', depth_image.app_depth_image,
        '/rgb_image', rgb_image.app_rgb_image,
        '/(.*)', 'index'
        )

# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
    #, initializer={'logged_in': False})

class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    # ============ Final da Inicializacao unica por classe ======

    def GET(self, name):
        web.header('Content-Type', 'application/xml')
        
        # autorizacao.
        server_timeout,client_timeout,client_username\
            =http_util.http_authorization(global_data.host_auth\
            ,global_data.access_token\
            ,http_util.http_get_token_in_header(web))    
        # resposta.
        if server_timeout<=0 or client_timeout<=0:
            web.ctx.status='401 Unauthorized'
            return
        
        t0 = int(time.time() * 1000)
        recurso_rdfxml=self.closest_point()
        web.debug('GET total time: ' + str(int(time.time() * 1000) - t0) + " ms")
        return recurso_rdfxml

    def closest_point(self):
        # Lendo dados de profundidade.
        depth, timestamp = freenect.sync_get_depth()

        resource = {}

        # Menor distancia.
        # No Kinect zero eh um ponto infinitamente longe e 2047 indica erro no pixel.
        # Calculando valores minimos nao nulos por coluna.
        discard_h = 20 # de cada lado da largura.
        mins = depth[:,discard_h:-discard_h].min(0)

        for j in range(mins.shape[0]):
            if mins[j] == 0:
                # Procurando menor valor nao nulo da coluna j.
                min_value = 2046
                for i in range(depth.shape[0]):
                    # Valor minimo nao nulo, nem erro.
                    if depth[i,j+discard_h] > 0 \
                        and depth[i,j+discard_h] < min_value:
                        min_value = depth[i,j+discard_h]

#                print "0 -> " + str(min_value) + "  j = " + str(j)
                mins[j] = min_value

        min_col = mins.argmin()

        # mudando escala da distancia Z para cm.
        z1 = 0.1236 * math.tan(mins[min_col] / 2842.5 + 1.1863)
        z2 = 1.0/((mins[min_col] * (-0.0030711016)) + 3.3309495161)
        z_m = ((z1+z2)/2.0)*100 # em cm
        resource["id"] = int(time.time() * 1000)
        resource["depth_closest"] = mins[min_col]
        resource["depth_closest_cm"] = z_m
        resource["col_closest"] = min_col + discard_h
        resource["screen_cols"] = depth.shape[1]
        resource["screen_rows"] = depth.shape[0]


#    def repulsive_force(self, mins):
        # "forca repulsiva" resultante.
        distances_2d = numpy.zeros((mins.shape[0],2))
        for j in range(mins.shape[0]):
            # mudando intervalo X de [0,600] para [300,-300]
            x = (-1)*(j-int(mins.shape[0]/2))
	    # calculando theta a partir de x e da constante y0.
            y0 = 564.21793960389959
	    theta_rad = math.atan(x/y0)
            # mudando escala da distancia Z para cm.
            z1 = 0.1236 * math.tan(mins[j] / 2842.5 + 1.1863)
	    z2 = 1.0/((mins[j] * (-0.0030711016)) + 3.3309495161)
#	    print "z0 = "+str(mins[j]) + "  z1 = " + str(z1) + " z2 = " + str(z2)
	    z_m = ((z1+z2)/2.0)*100 # em cm   #mins[j]
            # modulo da "forca" proporcional ao inverso do quadrado da distancia.
            z = 10000.0/z_m**2
	    # convertendo de r e theta (coord.cilindricas) para x,y (cartesianas)
	    x = z*math.cos(theta_rad)
	    y = z*math.sin(theta_rad)
            distances_2d[j,0] = x		
            distances_2d[j,1] = y

        # calculando "forca" resultante.
        fr = distances_2d.sum(0)
        # vetor de saida.
        ang_r = math.atan(fr[1]/fr[0])
        ang_d = ang_r*360.0/(2*numpy.pi)
        resource["repulsive_vector"] = "(" + str(fr[0]) + "," + str(fr[1]) + ")"
        resource["repulsive_module"] = str(math.sqrt(fr[0]**2 + fr[1]**2))
        resource["angle_rad"] = str(ang_r)
        resource["angle_deg"] = str(ang_d)
        # Log
        t0 = int(time.time() * 1000)
#        print "log... \n" + str(vector_dict)

        # log no servico stm
        resource_rdfxml=xml_util.dict_to_rdfxml(resource,"kinect")
        xml_response=http_util.http_request('post'\
            ,global_data.host_stm,"/"\
            ,None,global_data.access_token,resource_rdfxml)
                    
        return resource_rdfxml

    def __done__(self):
        # encerrando libfreenect.
        raise freenect.Kill



application = web.application(urls, globals())

if __name__ == "__main__":
    
    global_data.access_token="anonymous"
    global_data.realm="realm@som4r.net"
    global_data.user="kinect"
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