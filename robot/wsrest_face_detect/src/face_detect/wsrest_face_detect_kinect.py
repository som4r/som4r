#! /usr/bin/python

__author__="marcus"
__date__ ="$Aug 22, 2011 5:36:00 PM$"


import web
import cStringIO
import time
import urllib2
import os

import xml_util
import http_util
import global_data


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
    "num_faces" : 0, \
    "screen_width" : "", \
    "screen_height" : "", \
    "response_time" : 0, \
    "id" : 0 \
    }

# ToDo: implementar seguranca de acesso usando sessao.
#session = web.session.Session(app, web.session.DiskStore('sessions'))
    #, initializer={'logged_in': False})

class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.

    url_wsr_kinect_rgb = "http://localhost:8094/rgb_image/"

#    # Conectando com o BD.
#    db = db_util.connect()

    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):

#        web.header('Content-Type', 'application/xml')
        global resource
        
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

        # Chamada get sem parametro.
        if not name:
            web.header('Content-Type', 'application/xml')
            
            # Detectar faces.
            result = self.detect_and_draw()
                              
#            resource_xml = xml_util.dict_to_rdfxml(result, "face_detect")
            # Gravar no BD quando detectar faces.
            if result['num_faces'] > 0:
#                db_util.persist_resource(self.db, 'face_detect', resource_xml)
                
                # log no servico stm
                resource_rdfxml=xml_util.dict_to_rdfxml(result,"face_detect")
                xml_response=http_util.http_request('post'\
                    ,global_data.host_stm,"/"\
                    ,None,global_data.access_token,resource_rdfxml)

            web.debug("GET time: " + str(int(time.time() * 1000) - t0) + "ms")
            return resource_xml

        # Chamada com nome do arquivo solicitado.
        else:
            full_image_path = (snapshot_faces_dir + name)
            try:
                # retornando a partir do arquivo gravado.
                f=open(full_image_path,"rb")
                web.header('Content-Type', 'image/png')
                return f.read()
            except IOError:
                # arquivo nao existe.
                web.debug("no file")
                web.header('Content-Type', 'application/xml')
                return "<error>file not found</error>"
            finally:
                web.debug("GET time: " + str(int(time.time() * 1000) - t0) + "ms")

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
        # inserindo o token no header
        req=urllib2.Request(self.url_wsr_kinect_rgb)
        req.add_header("Authenticate",("token="+global_data.access_token))
        file=urllib2.urlopen(req)
#        file = urllib.urlopen(self.url_wsr_kinect_rgb)

        # close?
        # urllib2 module sends HTTP/1.1 requests with Connection:close header included.
        
        # Convertendo para formato PIL
        im=cStringIO.StringIO(file.read())
        pil_img=Image.open(im)
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
        resource_result = {}
        # Identificador unico da resposta.
        id_response = int(time.time() * 10000) # decimo de milesimo de segundo.
        resource_result['id'] = id_response
        # Populando recurso resultado.
#        resource_result['_max_num_faces'] = resource_params['_max_num_faces']
        resource_result["image_full"] = str(id_response) + "_full.png"
        resource_result['screen_width'] = str(img.width)
        resource_result['screen_height'] = str(img.height)

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

            faces_dict={}
            num_faces = 0
            # loop das faces detectadas
            if faces:

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
                    face_name="face"+str(num_faces)
                    faces_dict[face_name+"_x"]=str(x1+dx1)
                    faces_dict[face_name+"_y"]=str(y1+dy1)
                    faces_dict[face_name+"_sx"]=str(int(x2+dx2-(x1+dx1)))
                    faces_dict[face_name+"_sy"]=str(int(y2+dy2-(y1+dy1)))
                    
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
                        + str(id_response) + "_face" + str(num_faces) + ".png"
                    cvSaveImage(filename, final_gray)

                    faces_dict[face_name+"_filename"]=filename
                    
                    num_faces = num_faces + 1
                    
                web.debug('faces count = ' + str(num_faces))
#                web.debug('details of faces: ' + str(faces_dict))

                # gravar imagem completa.
                if num_faces > 0:
                    filename = snapshot_faces_dir \
                        + str(id_response) + "_full" + ".png"
                    cvSaveImage(filename, img)

            resource_result['num_faces'] = num_faces
            resource_result['faces'] = faces_dict


        t0 = int(time.time() * 1000) - t0
#        web.debug('detect draw total time: ' + str(t0) + " ms")
        resource_result['response_time'] = t0

        return resource_result

#    def __done__(self):
#        # disconnect from server
#        self.db.close()

application = web.application(urls, globals())

if __name__ == "__main__":
    
    global_data.access_token="anonymous"
    global_data.realm="realm@som4r.net"
    global_data.user="face_detect"
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

# Comando para rodar no apache.
#application = web.application(urls, globals()).wsgifunc()
