#ifdef _WIN32
#include <windows.h>
#endif
#include <stdio.h>
#include <stdlib.h>
#ifndef __APPLE__
#include <GL/gl.h>
#include <GL/glut.h>
#else
#include <OpenGL/gl.h>
#include <GLUT/glut.h>
#endif
#include <AR/gsub.h>
#include <AR/video.h>
#include <AR/param.h>
#include <AR/ar.h>


/*
MYSQL *mysql_init(MYSQL *mysql)
MYSQL *mysql_real_connect(MYSQL *mysql, const char *host, const char
 *user, const char *passwd, const char *db,
 unsigned int port, const char *unix_socket, unsigned int client_flag)
char *mysql_error(MYSQL *mysql)
int mysql_select_db(MYSQL *mysql, const char *db)
int mysql_real_query(MYSQL *mysql, const char *query, unsigned long
length)
char *strmov(register char *dst, register const char *src)
 */

#include <math.h>
#include <string.h>
#include <mysql/mysql.h>

//
// Camera configuration.
//
#ifdef _WIN32
char *vconf = "Data\\WDM_camera_flipV.xml";
#else
char *vconf = "";
#endif

int xsize, ysize;
int thresh = 100;
int count = 0;

char *cparam_name = "Data/camera_para.dat";
ARParam cparam;

char *patt_name = "Data/patt.hiro";
int patt_id;
double patt_width = 80.0;
double patt_center[2] = {0.0, 0.0};
double patt_trans[3][4];

MYSQL mysql;
int xyz_old[3] = {0,0,0};

static void init(void);
static void cleanup(void);
static void keyEvent(unsigned char key, int x, int y);
static void mainLoop(void);
static void draw(void);
double round(double val);
//static int mysql_exec_sql(MYSQL mysql,const char create_definition);
/*helper fuction */
//int mysql_exec_sql(MYSQL mysql,const char create_definition)
//{
//   return mysql_real_query(mysql,create_definition,strlen(create_definition));
//}

int main(int argc, char **argv) {
    glutInit(&argc, argv);
    init();

    arVideoCapStart();
    argMainLoop(NULL, keyEvent, mainLoop);
    return (0);
}

double round(double x) {
  return ((x - floor(x)) >= 0.5) ? ceil(x) : floor(x);
}

static void keyEvent(unsigned char key, int x, int y) {
    /* quit if the ESC key is pressed */
    if (key == 0x1b) {
        printf("*** %f (frame/sec)\n", (double) count / arUtilTimer());
        cleanup();
        exit(0);
    }
}

/* main loop */
static void mainLoop(void) {
    ARUint8 *dataPtr;
    ARMarkerInfo *marker_info;
    int marker_num;
    int j, k;

    double cam_trans[3][4];

    /* grab a vide frame */
    if ((dataPtr = (ARUint8 *) arVideoGetImage()) == NULL) {
        arUtilSleep(2);
        return;
    }
    if (count == 0) arUtilTimerReset();
    count++;

    argDrawMode2D();
    argDispImage(dataPtr, 0, 0);

    /* detect the markers in the video frame */
    if (arDetectMarker(dataPtr, thresh, &marker_info, &marker_num) < 0) {
        cleanup();
        exit(0);
    }

    arVideoCapNext();

    /* check for object visibility */
    k = -1;
    for (j = 0; j < marker_num; j++) {
        if (patt_id == marker_info[j].id) {
            if (k == -1) k = j;
            else if (marker_info[k].cf < marker_info[j].cf) k = j;
        }
    }
    if (k == -1) {
        argSwapBuffers();
        return;
    }

    /* get the transformation between the marker and the real camera */
    arGetTransMat(&marker_info[k], patt_center, patt_width, patt_trans);
    arUtilMatInv(patt_trans, cam_trans);

    double fator = 0.01;  // 1=parte inteira da leitura;  100=precisao da leitura.
    int x = round(cam_trans[0][3] * fator);
    int y = round(cam_trans[1][3] * fator);
    int z = round(cam_trans[2][3] * fator);
    if (xyz_old[0]==x && xyz_old[1]==y && xyz_old[2]==z);
    else {
        /* Gravando leitura do marcador */
        char record[1000];
        sprintf(record,"INSERT INTO tbl_landmark_position"
                " (read_datetime,id_landmark,x,y,z) VALUES "
                "(now(),1, %10.2f ,%10.2f ,%10.2f)",
                cam_trans[0][3], cam_trans[1][3], cam_trans[2][3]);
//            " RAW: Cam Pos x: %3.1f  y: %3.1f  z: %3.1f",
//            cam_trans[0][3], cam_trans[1][3], cam_trans[2][3]);
//    sprintf(record,"INSERT INTO tbl_landmark_position (read_datetime,id_landmark,x,y,z) VALUES (now(),1, 3, 3, 3)");
//    if(mysql_exec_sql(&mysql,record)==0)/*success*/
        if (mysql_real_query(&mysql,record,strlen(record))==0)
            printf( "Record Added\n");
        else
            printf( "Failed to add records: Error: %s\n", mysql_error(&mysql));

        xyz_old[0]=x;
        xyz_old[1]=y;
        xyz_old[2]=z;
    }

    draw();

    argSwapBuffers();
}

static void init(void) {
    ARParam wparam;

    /* open the video path */
    if (arVideoOpen(vconf) < 0) exit(0);
    /* find the size of the window */
    if (arVideoInqSize(&xsize, &ysize) < 0) exit(0);
    printf("Image size (x,y) = (%d,%d)\n", xsize, ysize);

    /* set the initial camera parameters */
    if (arParamLoad(cparam_name, 1, &wparam) < 0) {
        printf("Camera parameter load error !!\n");
        exit(0);
    }
    arParamChangeSize(&wparam, xsize, ysize, &cparam);
    arInitCparam(&cparam);
    printf("*** Camera Parameter ***\n");
    arParamDisp(&cparam);

    if ((patt_id = arLoadPatt(patt_name)) < 0) {
        printf("pattern load error !!\n");
        exit(0);
    }

    /* open the graphics window */
    argInit(&cparam, 1.0, 0, 0, 0, 0);

    /* Abrindo conexao com BD*/
    if (mysql_init(&mysql)==NULL) {
	printf("\nFailed to initate MySQL connection");
	exit(1);
    }

    if (!mysql_real_connect(&mysql,"localhost","robot","123456",NULL,0,NULL,0)) {
        printf( "Failed to connect to MySQL: Error: %s\n",
        mysql_error(&mysql));
        exit(1);
    }

    if(mysql_select_db(&mysql,"robot")==0)/*success*/
        printf( "Database Selected\n");
    else
        printf( "Failed to connect to Database: Error: %s\n", mysql_error(&mysql));

}

/* cleanup function called when program exits */
static void cleanup(void) {
    arVideoCapStop();
    arVideoClose();
    argCleanup();
    mysql_close(&mysql);
}

static void draw(void) {
    double gl_para[16];
    GLfloat mat_ambient[] = {0.0, 0.0, 1.0, 1.0};
    GLfloat mat_flash[] = {0.0, 0.0, 1.0, 1.0};
    GLfloat mat_flash_shiny[] = {50.0};
    GLfloat light_position[] = {100.0, -200.0, 200.0, 0.0};
    GLfloat ambi[] = {0.1, 0.1, 0.1, 0.1};
    GLfloat lightZeroColor[] = {0.9, 0.9, 0.9, 0.1};

    argDrawMode3D();
    argDraw3dCamera(0, 0);
    glClearDepth(1.0);
    glClear(GL_DEPTH_BUFFER_BIT);
    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LEQUAL);

    /* load the camera transformation matrix */
    argConvGlpara(patt_trans, gl_para);
    glMatrixMode(GL_MODELVIEW);
    glLoadMatrixd(gl_para);

    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0);
    glLightfv(GL_LIGHT0, GL_POSITION, light_position);
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambi);
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor);
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_flash);
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_flash_shiny);
    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient);
    glMatrixMode(GL_MODELVIEW);
    glTranslatef(0.0, 0.0, 25.0);
    glutSolidCube(50.0);
    glDisable(GL_LIGHTING);

    glDisable(GL_DEPTH_TEST);
}
