# Installation Guide #

This document contains a list of prerequisites and web services required to run the SOM4R Middleware. Each link has detailed instructions on how to install the libraries and others prerequisites.

## Installing Prerequisites ##

  * [WEB Server and DBMS - Apache HTTPD, Php, Mysql, PhpMyAdmin](https://github.com/som4r/som4r/blob/master/wiki/installapachephpmysql.md)
  * [Speech Recognition Libraries and Text To Speech - CMU Sphinx, eSpeak](https://github.com/som4r/som4r/blob/master/wiki/installespeaksphinx.md)
  * [Libraries for MS-Kinect Sensor - OpenKinect](https://github.com/som4r/som4r/blob/master/wiki/installopenkinect.md)
  * [Content Management System - Joomla](https://github.com/som4r/som4r/blob/master/wiki/installjoomla.md)
  * [Python Libraries - WebPy, PyUSB](https://github.com/som4r/som4r/blob/master/wiki/installpythonlibraries.md)
  * [Face Detection Libraries - OpenCV](https://github.com/som4r/som4r/blob/master/wiki/installopencv.md)
  * [Augmented Reality Libraries - ARToolKit, Gstreamer](https://github.com/som4r/som4r/blob/master/wiki/installartoolkit.md)
  * [Media Server and Video Streaming  - Red5, FFmpeg, Xuggler](https://github.com/som4r/som4r/blob/master/wiki/installred5ffmpeg.md)

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
