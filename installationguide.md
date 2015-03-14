# Installation Guide #

This document contains a list of prerequisites and web services required to run the SOM4R Middleware. Each link has detailed instructions on how to install the libraries and others prerequisites.

## Installing Prerequisites ##

  * [WEB Server and DBMS - Apache HTTPD, Php, Mysql, PhpMyAdmin](https://code.google.com/p/som4r/wiki/installapachephpmysql)
  * [Speech Recognition Libraries and Text To Speech - CMU Sphinx, eSpeak](https://code.google.com/p/som4r/wiki/installespeaksphinx)
  * [Libraries for MS-Kinect Sensor - OpenKinect](https://code.google.com/p/som4r/wiki/installopenkinect)
  * [Content Management System - Joomla](https://code.google.com/p/som4r/wiki/installjoomla)
  * [Python Libraries - WebPy, PyUSB](https://code.google.com/p/som4r/wiki/installpythonlibraries)
  * [Face Detection Libraries - OpenCV](https://code.google.com/p/som4r/wiki/installopencv)
  * [Augmented Reality Libraries - ARToolKit, Gstreamer](https://code.google.com/p/som4r/wiki/installartoolkit)
  * [Media Server and Video Streaming  - Red5, FFmpeg, Xuggler](https://code.google.com/p/som4r/wiki/installred5ffmpeg)

## Installing SOM4R Web Services ##

  * Web Services and Applications
```
cd ~/
svn checkout http://som4r.googlecode.com/svn/ som4r
```
  * Autostart
    1. Edit _/etc/init.d/rc.local_ and include a call to file _robot\_autostart.sh_, located at _~/som4r/trunk/robot/config\_files/robot_
    1. Adjust path to webservices in the file _robot\_autostart.sh_
    1. Reboot operating system
> If it is all right, after reboot the robot will say "robot", and "ready" one minute later.