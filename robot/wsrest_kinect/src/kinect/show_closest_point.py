#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Jul 11, 2011 9:27:24 PM$"

import freenect
import numpy
import scipy
import math
import time
import xml_util
import httplib

if __name__ == "__main__":

    recurso = { \
#        "status" : "ready", \
#        "image_rgb" : "ToDo", \
#        "image_gray" : "ToDo", \
        "depth_closest" : "", \
#        "row_closest" : "", \
        "col_closest" : "", \
#        "screen_rows" : "", \
#        "screen_cols" : "", \
        "best_direction" : "", \
        "best_depth" : "", \
        "depth_closest_cm" : "", \
        "id" : 0 \
        }

    while True:

#        time.sleep(3)

        # Lendo dados de profundidade.
        depth, timestamp = freenect.sync_get_depth()


#        u,v = scipy.mgrid[:480:2,:640:2]
#        xyz,uv = calibkinect.depth2xyzuv(freenect.sync_get_depth()[::2,::2], u, v)
#        print 'xyz.shape = '
#        print xyz.shape
#
#        print 'uv.shape = '
#        print uv.shape

        # Menor distancia.
        # No Kinect zero eh um ponto infinitamente longe e 2047 indica erro no pixel.

        # A escala eh invertida, ou seja, quanto maior a leitura, mais perto.
        # Calculando valores maximos por coluna, nao erro.
#        maxs = depth[:,160:-160].max(0)
        discard_h = 20 # de cada lado da largura.
        mins = depth[:,discard_h:-discard_h].min(0)

        # Substituindo erro pela media da coluna.
#        for j in range(maxs.shape[0]):
#            if maxs[j] == 2047:
#                maxs[j] = int(numpy.mean(depth[:,j],axis=0))

        for j in range(mins.shape[0]):
            if mins[j] == 0:
                # Procurando menor valor nao erro (2047) da coluna j.
                min_value = 2046
                for i in range(depth.shape[0]):
                    if depth[i,j+discard_h] > 0 \
                        and depth[i,j+discard_h] < min_value:
                        min_value = depth[i,j+discard_h]

                print "0 -> " + str(min_value) + "  j = " + str(j)
                mins[j] = min_value

 #           else:
#                print "min = " + str(mins[j]) + "  j = " + str(j)

        min_col = mins.argmin()

        # Localizando linha (Y) do maior valor da coluna com valor maximo.
        max_row = 0
    #        for i in range(depth.shape[0]):
    #            if depth[i,max_col] == maxs[max_col]:
    #                max_row = i
    #                break

        recurso["id"] = timestamp
        recurso["depth_closest"] = mins[min_col]
        recurso["row_closest"] = max_row
        recurso["col_closest"] = min_col + discard_h
        recurso["screen_cols"] = depth.shape[1]
        recurso["screen_rows"] = depth.shape[0]
        
        min_depth = mins[min_col]
        recurso["depth_closest_cm"] = \
            0.1236 * math.tan(min_depth/2842.5 + 1.1863)
#            1.0 / (min_depth * -0.0030711016 + 3.3309495161)
#            (numpy.tan((min_depth / 1024 ) + 0.5) * 33.825) + 5.7

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
#            theta_g = theta_rad*360.0/(2*numpy.pi)
#	    print "x=" + str(x) + " y=" + str(y) + " z_c=" + str(z_c) \
#                + " j=" +str(j) + " f(z)="+str(z) \
#                + " theta_r=" + str(theta_rad) + " theta_g="+ str(theta_g)
        # calculando "forca" resultante.
        fr = distances_2d.sum(0)
#        recurso["strength_x"] = fr[0]
#        recurso["strength_y"] = fr[1]
        # vetor de saida.
        ang_r = math.atan(fr[1]/fr[0])
        ang_g = ang_r*360.0/(2*numpy.pi)

        vector_dict = { \
            "vetor resultante" : ("(" + str(fr[0]) + "," + str(fr[1]) + ")")\
            ,"modulo" : str(math.sqrt(fr[0]**2 + fr[1]**2))\
            ,"angulo rad" : str(ang_r)\
            ,"angulo graus" : str(ang_g)\
        }
        # Log
        t0 = int(time.time() * 1000)
        print "log... \n" + str(vector_dict)
        recursoXml = xml_util.dict_to_rdfxml(vector_dict, "closest_point")
        # Enviar ao WS.
        conn = httplib.HTTPConnection("localhost:8098")
        conn.request("POST", "/", recursoXml)
        response = conn.getresponse()
        conn.close()

        print "Time to post log: " \
            + str(int(time.time() * 1000) - t0) + "ms"


        middle_point = int(mins.shape[0]/2)
        # Calcula as areas a direita e esquerda do ponto central
        area_left = mins[:middle_point].sum()
        area_right = mins[middle_point:].sum()
        # Calcula as areas a direita e esquerda do ponto mais proximo.
#        area_left = maxs[:max_col].sum()
#        area_right = maxs[max_col:].sum()
#        print "area left = " + str(area_left)
#        print "area right = " + str(area_right)
        # Melhor direcao a seguir (maior distancia da maior area.)
        if area_left > area_right:
            best_col_2_go = mins[:middle_point].argmax()
            best_depth = mins[best_col_2_go]
        else:
            best_col_2_go = mins[middle_point:].argmax() + middle_point
            best_depth = mins[best_col_2_go]
        recurso["best_direction"] = best_col_2_go + discard_h
        recurso["best_depth"] = best_depth

        print " "
        print "========================"
        print recurso
        print "========================"
        print " "

#        break
        time.sleep(10)


    print "================= Final"
