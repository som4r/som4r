#! /usr/bin/python

__author__="marcus"
__date__ ="$Aug 22, 2011 5:36:00 PM$"


import web
import StringIO
import cStringIO
import time
import MySQLdb
import urllib
import os


"""
This program is demonstration for face and object detection using haar-like features.
The program finds faces in a camera image or video stream and displays a red box around them.

Original C implementation by:  ?
Python implementation by: Roman Stanchak
"""

from opencv.cv import *
from opencv.highgui import *
from PIL import Image
from opencv import adaptors


# Global Variables
cascade = None
capture = None
storage = cvCreateMemStorage(0)
cascade_name = "./haarcascades/haarcascade_frontalface_alt.xml"
input_name = "../c/lena.jpg"

# Parameters for haar detection
# From the API:
# The default parameters (scale_factor=1.1, min_neighbors=3, flags=0) are tuned
# for accurate yet slow object detection. For a faster operation on real video
# images the settings are:
# scale_factor=1.2, min_neighbors=2, flags=CV_HAAR_DO_CANNY_PRUNING,
# min_size=<minimum possible face size
min_size = cvSize(20,20)
image_scale = 1.3
haar_scale = 1.2
min_neighbors = 2
haar_flags = CV_HAAR_DO_CANNY_PRUNING #0


init_opencv = True

urls = (
        '/(.*)', 'index'
        )

web.config.debug = True    # Debug true causa problema quando usado junto com sessoes.

snapshot_faces_dir = os.environ['HOME'] + "/robot_/faces/"
resource_name = "FaceDetection"
resource = { \
    "status" : "ready", \
    "image_name_" : "", \
    "num_faces_" : 0, \
    "details_faces_" : "", \
    "screen_width_" : "", \
    "screen_height_" : "", \
    "response_time_" : 0, \
    "id_" : 0 \
    }            # details_faces = formato "x=?:y=?:sx=?:sy=?_x=?:y=..."

# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
    #, initializer={'logged_in': False})

class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    url_wsr_kinect_rgb = "http://localhost:8094/rgb_image/"
#    url_wsr_kinect_rgb = "192.168.1.107:8080"
#    url_wsr_kinect_rgb = "192.168.20.101:8080"
#    url_wsr_kinect_rgb = "192.168.0.101:8080"

    # Conectando com o BD.
    db = MySQLdb.connect(
        host="localhost", port=3306, user="robot", passwd="123456", db="robot")
#        host="192.168.20.101", port=3306, user="robot", passwd="123456", db="robot")
#        host="192.168.0.101", port=3306, user="robot", passwd="123456", db="robot")

    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):

#        web.header('Content-Type', 'application/xml')
        global resource

        t0 = int(time.time() * 1000)

        # Chamada get sem parametro.
        if not name:
            web.header('Content-Type', 'application/xml')
            
            # Detectando faces.
            result = self.detect_and_draw()

            web.debug("GET time: " + str(int(time.time() * 1000) - t0) + "ms")
            return self.to_xml(result)

        # Chamada com nome do arquivo solicitado.
        else:
            full_image_path = (snapshot_faces_dir + name)
            try:
                # retornando a partir do arquivo gravado.
                f = open(full_image_path,"rb")
                web.header('Content-Type', 'image/png')
                return f.read()
            except IOError:
                # arquivo nao existe.
                web.debug("no file")
                web.header('Content-Type', 'application/xml')
                return "<error>file not found</error>"
            finally:
                web.debug("GET time: " + str(int(time.time() * 1000) - t0) + "ms")
            
#    def POST(self, name):
#        t0 = int(time.time() * 1000)
#
#        # Criando copia do recurso global com dados do post.
#        resource1 = self.xml_to_resource(web.data())
#
#        result = self.detect_and_draw(resource1.copy())
##        self.persist()
#
#        web.debug("POST time: " + str(int(time.time() * 1000) - t0) + "ms")
#
#        return result


    def xml_to_resource(self, xml):
        # ToDo: Usar api xml do python.
        # ToDo: Remover tudo que nao estiver dentro da tag do recurso
        global resource
        # Criando copia do recurso global com o parametro xml.
        resource1 = resource.copy()
        # Procura pelos itens do recurso, ignorando os outros dados do xml.
        for item in resource1.items():
            key, value = item
            # Ignorando atributos: status
#            if key != 'status':
            inicio = xml.find("<" + key + ">")
            if inicio >= 0:
                final = xml.find("</" + key + ">")
                if inicio >= 0 and final > inicio:
                    stringXml = xml[inicio + len(key) + 2 : final]
                    if len(stringXml) > 0: # Ignorando chaves vazias.
                        # Tipo do recurso (string, float ou int)
                        if isinstance(resource1[key], int):
                            resource1[key] = int(stringXml)
                        if isinstance(resource1[key], float):
                            resource1[key] = float(stringXml)
                        else:   #String (default)
                            resource1[key] = str(stringXml)

#                        web.debug("key:value = " + key + " : " + str(resource1[key]))
        return resource1

    def empty_resource(self, resource_sample):
        # ToDo: Usar api xml do python.
        # ToDo: Remover tudo que nao estiver dentro da tag do recurso_nome
        resource1 = resource_sample.copy()
        # Procura pelos itens do recurso, ignorando os outros dados do xml.
        for item in resource1.items():
            key, value = item
            # Tipo do recurso (string, float ou int)
            if isinstance(resource1[key], int):
                resource1[key] = 0
            if isinstance(resource1[key], float):
                resource1[key] = 0.0
            else:   #String (default)
                resource1[key] = ""
        return resource1

    def to_xml(self, resource):
        global resource_name
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
#        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  resource_name)

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % resource_name)
        stream.seek(0)
        return stream.read()

    def detect_and_draw(self):#, resource_params):

#        web.debug('detect draw')
        t0 = int(time.time() * 1000)

        global init_opencv, cascade, capture, storage
        if init_opencv:
            init_opencv = False
            # the OpenCV API says this function is obsolete, but we can't
            # cast the output of cvLoad to a HaarClassifierCascade, so use this anyways
            # the size parameter is ignored
            cascade = cvLoadHaarClassifierCascade( cascade_name, cvSize(1,1) );

            if not cascade:
                web.debug("ERROR: Could not load classifier cascade")
                raise ValueError('[ERRO] Could not load classifier cascade.')


        frame_copy = None

        # Buscando imagem atual do servico kinect (rgb snapshot).
        file = urllib.urlopen(self.url_wsr_kinect_rgb)
        # Convertendo para formato PIL
        im = cStringIO.StringIO(file.read())
        pil_img = Image.open(im)
        # Convertendo de formato PIL para IPL-OpenCv.
        frame = adaptors.PIL2Ipl(pil_img)

        if( not frame ):
            web.debug("[INFO]  Not a frame")
        if( not frame_copy ):
            frame_copy = cvCreateImage( cvSize(frame.width,frame.height), \
                IPL_DEPTH_8U, frame.nChannels )
        if( frame.origin == IPL_ORIGIN_TL ):
            cvCopy( frame, frame_copy )
        else:
            cvFlip( frame, frame_copy, 0 )

        img = frame_copy

        # Criando copia default do recurso passado como parametro.
        global resource
        resource_result = self.empty_resource(resource.copy())
        # Identificador unico dac resposta.
        id_response = int(time.time() * 1000)
        resource_result['id_'] = id_response
        # Populando recurso resultado.
#        resource_result['_max_num_faces'] = resource_params['_max_num_faces']
        resource_result["image_name_"] = str(id_response) + "_.png"
        resource_result['screen_width_'] = str(img.width)
        resource_result['screen_height_'] = str(img.height)

        # allocate temporary images
        gray = cvCreateImage( cvSize(img.width,img.height), 8, 1 )
        small_img = cvCreateImage( cvSize( cvRound (img.width/image_scale), \
            cvRound (img.height/image_scale)), 8, 1 )
        # convert color input image to grayscale
        cvCvtColor( img, gray, CV_BGR2GRAY )
        # scale input image for faster processing
        cvResize( gray, small_img, CV_INTER_LINEAR )
#
        cvEqualizeHist( small_img, small_img )

        cvClearMemStorage( storage )

        if( cascade ):
#                t = cvGetTickCount()
            t = int(time.time() * 1000)
#                for i in range(1,6):
#                    cvClearMemStorage( storage )
            faces = cvHaarDetectObjects( small_img, cascade, storage,
                haar_scale, min_neighbors, haar_flags, min_size )
#                t = cvGetTickCount() - t
            t = int(time.time() * 1000) - t
#                print "detection time = %gms" % (t/(cvGetTickFrequency()*1000.))
            web.debug('detection time = ' + str(t) + 'ms   image_scale = ' \
                + str(image_scale))

            details_faces = ""

            if faces:
                num_faces = 0
                for r in faces:
#                        pt1 = cvPoint( int(r.x*image_scale), int(r.y*image_scale))
#                        pt2 = cvPoint( int((r.x+r.width)*image_scale), int((r.y+r.height)*image_scale) )
                    x1 = int(r.x*image_scale)
                    x2 = int((r.x+r.width)*image_scale)
                    dx1 = int(r.width*image_scale*0.12)
                    dx2 = (-1)*int(r.width*image_scale*0.13)
                    lx = int(x2+dx2-(x1+dx1))
                    ly = int(lx * 1.2 )
#                        ly = int(y2+dy2-(y1+dy1))
                    y1 = int(r.y*image_scale)
                    dy1 = int(r.height*image_scale*0.17)
                    pt1 = cvPoint( x1 + dx1 , y1 + dy1 )
                    y2 = y1+dy1 + ly
#                        y2 = int((r.y+r.height)*image_scale)
                    dy2 = 0 # int(r.height*image_scale*0.05)
                    pt2 = cvPoint( x2 + dx2 , y2 + dy2 )

#                        cvRectangle( gray, pt1, pt2, CV_RGB(255,0,0), 2, 8, 0 );

                    details_faces = details_faces \
                        + "x=" + str(x1+dx1) \
                        +":y=" + str(y1+dy1) \
                        + ":sx=" + str(int(x2+dx2-(x1+dx1))) \
                        + ":sy=" + str(int(y2+dy2-(y1+dy1))) + "_"
                    face_position_screen = \
                        "_x" + str(x1+dx1) \
                        +"_y" + str(y1+dy1) \
                        + "_sx" + str(int(x2+dx2-(x1+dx1))) \
                        + "_sy" + str(int(y2+dy2-(y1+dy1))) \
                        + "_sw" + resource_result['screen_width_'] \
                        + "_sh" + resource_result['screen_height_']
                    # sub-image
                    sub_image = cvCreateImage( \
                        (lx, ly), 8, 1)  # Parameters overwritten anyway...
                    sub_image = cvGetSubRect( img \
                        , ( x1+dx1, y1+dy1 , lx, ly ) )

                    sub_gray = cvCreateImage( \
                        cvSize(sub_image.width,sub_image.height), 8, 1 )

                    final_gray = cvCreateImage( \
                        cvSize(125, 150), 8, 1 )

                    # convert color input image to grayscale
                    cvCvtColor( sub_image, sub_gray, CV_BGR2GRAY )

                    # scale input image for faster processing
                    cvResize( sub_gray, final_gray, CV_INTER_LINEAR )
        #
#                        cvEqualizeHist( final_gray, final_gray )
                    # Gravando faces detectadas.
                    #cvSaveImage("/home/marcus/Desktop/faces/"
#                        cvSaveImage("/var/www/portal/images/faces/"
                    filename = snapshot_faces_dir \
                        + str(id_response) + "_face" + str(num_faces)\
                        + face_position_screen + ".png"
                    cvSaveImage(filename, final_gray)#img)

                    num_faces = num_faces + 1
                    
                web.debug('faces count = ' + str(num_faces))
                web.debug('details of faces: ' + details_faces)

                resource_result['num_faces_'] = num_faces
                resource_result['details_faces_'] = details_faces

                # ToDo:
                # gravar imagem completa.

        t0 = int(time.time() * 1000) - t0
        web.debug('detect draw total time: ' + str(t0) + " ms")
        resource_result['response_time_'] = t0

        return resource_result

    #    def __done__(self):

    def persist(self):
        global recurso
        cursor = self.db.cursor()
        # Prepare SQL query to INSERT a record into the database.
        sql = """INSERT INTO tbl_stm (service, xml_resource)
                 VALUES ('face_detect', '%s')""" % (self.to_xml(recurso))
#        print sql
        try:
           # Execute the SQL command
           cursor.execute(sql)
           # Commit your changes in the database
           self.db.commit()
        except:
           # Rollback in case there is any error
           self.db.rollback()


    def __done__(self):
        # disconnect from server
        self.db.close()

application = web.application(urls, globals())

if __name__ == "__main__":
    application.run()

#application = web.application(urls, globals()).wsgifunc()
