# som4r
### Simple and Open Middleware for Robotics

A middleware that shares resources (sensors, actuators and services) of one or more robots through the TCP/IP network. This middleware provides greater efficiency in the development of software applications for robotics, including hardware abstraction, communication reliability, scalability, security, the ability to integrate system actuators and sensors, and easily incorporate several widely used open-source libraries for specific tasks or sensors, like OpenCV, ARToolKit, OpenKinect, eSpeak, CMU Sphinx and PyFaces, all of them used in this project.

### Article

Veloso, M.V.D., Filho, J.T.C. & Barreto, G.A. J Intell Robot Syst (2017). doi:10.1007/s10846-017-0504-y , available at http://rdcu.be/pwPf

### Preliminary experiments:

In order to evaluate the performance of the proposed middleware, SOM4R, we present preliminary experiments with the developed applications, built specifically for an autonomous wheeled mobile robot, by integrating voice command functionality, obstacle detection and avoidance, greeting a person, automatic battery recharge, teleoperation, text-to-speech, and a web based human machine interface (HMI).

 * [Video 1 - Joystick Android App Test](https://www.youtube.com/watch?v=G2iMuNAkWkE)
 * [Video 2 - Joystick Android App Test - Pioneer P3DX robot](https://www.youtube.com/watch?v=bSoOqbzGmYQ)
 * [Video 3 - Prototype tests - Our own robot, made from scratch.](https://www.youtube.com/watch?v=vqF8QrWX6LU)
 * [Video 4 - Presentation to Governor of the state - Voice Command, Joytstick, Augmented reality](https://www.youtube.com/watch?v=InUTArXFyMc)
 * [Video 5 - Web based HMI - Depth Image Module Test](https://www.youtube.com/watch?v=CSv3zVnXd0k)


## Installation Guide

This document is a guide for installing a list of prerequisites and the web services required to run the SOM4R Middleware. Each link has detailed instructions on how to install the libraries and others prerequisites on Ubuntu Linux. See also [Videos](https://github.com/som4r/som4r/blob/master/wiki/videos.md) and [FAQ](https://github.com/som4r/som4r/blob/master/wiki/faq.md).

### Installing Prerequisites

  * [WEB Server and DBMS - Apache HTTPD, Php, Mysql, PhpMyAdmin](https://github.com/som4r/som4r/blob/master/wiki/installapachephpmysql.md)
  * [Speech Recognition Libraries and Text To Speech - CMU Sphinx, eSpeak](https://github.com/som4r/som4r/blob/master/wiki/installespeaksphinx.md)
  * [Libraries for MS-Kinect Sensor - OpenKinect](https://github.com/som4r/som4r/blob/master/wiki/installopenkinect.md)
  * [Content Management System - Joomla](https://github.com/som4r/som4r/blob/master/wiki/installjoomla.md)
  * [Python Libraries - WebPy, PyUSB](https://github.com/som4r/som4r/blob/master/wiki/installpythonlibraries.md)
  * [Face Detection Libraries - OpenCV](https://github.com/som4r/som4r/blob/master/wiki/installopencv.md)
  * [Augmented Reality Libraries - ARToolKit, Gstreamer](https://github.com/som4r/som4r/blob/master/wiki/installartoolkit.md)
  * [Media Server and Video Streaming  - Red5, FFmpeg, Xuggler](https://github.com/som4r/som4r/blob/master/wiki/installred5ffmpeg.md)


### Creating SOM4R default database

  * Download and create a database using default script for MySQL (folder /som4r/robot/database_create_script).

### Installing SOM4R Web Services

  * Web Services and Applications
```
cd ~/
git clone http://github.com/som4r/som4r
```
  * Autostart
    1. Edit _/etc/init.d/rc.local_ and include a call to file _robot\_autostart.sh_, located at _~/som4r/trunk/robot/config\_files/robot_
    1. Adjust path to webservices in the file _robot\_autostart.sh_
    1. Reboot operating system
> If the installation was done successfully, after reboot has completed, the robot will say the word "robot" and, one minute later, the word "ready".
