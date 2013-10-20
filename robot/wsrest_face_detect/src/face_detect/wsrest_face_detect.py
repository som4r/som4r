#! /usr/bin/python

__author__="marcus"
__date__ ="$Mar 7, 2011 6:29:42 PM$"


import web
import StringIO
import time
import MySQLdb


"""
This program is demonstration for face and object detection using haar-like features.
The program finds faces in a camera image or video stream and displays a red box around them.

Original C implementation by:  ?
Python implementation by: Roman Stanchak
"""

from opencv.cv import *
from opencv.highgui import *


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

recurso = { \
    "status" : "ready", \
    "imagem" : "ToDo", \
    "posicao_x" : "", \
    "posicao_y" : "", \
    "tamanho_x" : "", \
    "tamanho_y" : "", \
    "screen_width" : "", \
    "screen_height" : "", \
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
        host="localhost", port=3306, user="robot", passwd="123456", db="robot")
#        host="192.168.20.101", port=3306, user="robot", passwd="123456", db="robot")
#        host="192.168.0.101", port=3306, user="robot", passwd="123456", db="robot")

    # ============ Final da Inicializacao unica por classe =================

    def GET(self, name):

        web.header('Content-Type', 'application/xml')
        global recurso

        tg = int(time.time() * 1000)

        self.detect_and_draw()
        self.persist()

        # ToDo: Nao aceitar chamada get com parametro.
#        if not name:
#            name = 'World.'
        tg = int(time.time() * 1000) - tg
        web.debug('GET total time: ' + str(tg) + " ms")

        return self.to_xml(recurso)

    def to_xml(self, resource):
        """ Transform a dict into a XML, writing to a stream """
        stream = StringIO.StringIO()
#        stream.write("<?xml version='1.0' encoding='UTF-8'?>")
        stream.write('<%s>' %  "FaceDetectRO")

        for item in resource.items():
            key, value = item
            if isinstance(value, str) or isinstance(value, unicode):
                stream.write('\n<%s>%s</%s>' % (key, value, key))
            else:
                stream.write('\n<%s>%d</%s>' % (key, value, key))

        stream.write('\n</%s>' % "FaceDetectRO")
        stream.seek(0)
        return stream.read()

    def detect_and_draw(self, resource_params):

#        web.debug('detect draw')
        t0 = int(time.time() * 1000)

        global init_opencv, cascade, capture, storage, resource

        if init_opencv:
            init_opencv = False
            # the OpenCV API says this function is obsolete, but we can't
            # cast the output of cvLoad to a HaarClassifierCascade, so use this anyways
            # the size parameter is ignored
            cascade = cvLoadHaarClassifierCascade( cascade_name, cvSize(1,1) );
            if not cascade:
                web.debug("ERROR: Could not load classifier cascade")
                raise ValueError('[ERRO] Could not load classifier cascade.')
            capture = cvCreateCameraCapture( 0 )
            storage = cvCreateMemStorage(0)

        if( capture ):

            web.debug('capture ok')
            frame_copy = None

            frame = cvQueryFrame( capture )
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

#            recurso['posicao_x'] = ""
#            recurso['posicao_y'] = ""
#            recurso['tamanho_x'] = ""
#            recurso['tamanho_y'] = ""
            recurso['screen_width'] = str(img.width)
            recurso['screen_height'] = str(img.height)

            recurso['id'] = str(int(time.time() * 1000))
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

                        recurso['posicao_x'] = str(x1+dx1)
                        recurso['posicao_y'] = str(y1+dy1)
                        recurso['tamanho_x'] = str(int(x2+dx2-(x1+dx1)))
                        recurso['tamanho_y'] = str(int(y2+dy2-(y1+dy1)))
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
                        cvSaveImage("/home/marcus/python_test/pyfaces/gallery/" \
                            + str(int(time.time() * 1000)) \
                            + "_face.png", final_gray)#img)

                        num_faces = num_faces + 1
                    web.debug('faces count = ' + str(num_faces))




    #        cvShowImage( "result", img );

            t0 = int(time.time() * 1000) - t0
            web.debug('detect draw total time: ' + str(t0) + " ms")

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

    def cropImg(img, newSize, newCorner=(0, 0)):
	size = cv.GetSize(img)
	m = [[1, 0, size[0] / 2 + newCorner[0]],
            [0, 1, size[1] / 2 + newCorner[1]]]
	transl = cv.CreateMat(2, 3, cv.CV_32FC1)

	cv.mSet(transl, 0, 0, m[0][0])
	cv.mSet(transl, 1, 1, m[1][1])
	cv.mSet(transl, 0, 1, m[0][1])
	cv.mSet(transl, 0, 2, m[0][2])
	cv.mSet(transl, 1, 2, m[1][2])
	cv.mSet(transl, 1, 0, m[1][0])

	newImg = cv.CloneImage(img)
	cv.GetQuadrangleSubPix(img, newImg, transl)
	return newImg


    def __done__(self):
        # disconnect from server
        self.db.close()

application = web.application(urls, globals())

if __name__ == "__main__":
    application.run()

#application = web.application(urls, globals()).wsgifunc()
