# Introduction #

This document explains how to install OpenCV libraries needed by the SOM4R.


# Details #

This installation guide was tested on Ubuntu 10.10 with OpenCV 2.3 and Python 2.6.5. It also can be used as a guideline to install these components on others Linux distributions using similar packages.

## Libraries Installation ##

Installing the libraries that is needed by the SOM4R Vehicle WS software.
Running scripts on Terminal window:
```
# root access
sudo -i
apt-get update

# Install
apt-get install build-essential pkg-config libavcodec-dev libavformat-dev libjpeg62-dev libtiff4-dev cmake libswscale-dev libjasper-dev python-opencv libgtk2.0-dev python-opencv python-dev

# Download
cd /opt
wget http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.3/OpenCV-2.3.0.tar.bz2

# Decompress
tar xvf OpenCV-2.3.0.tar.bz2
cd OpenCV-2.3.0

# CMake (must returns FFMPEG = 1)
cmake -D BUILD_PYTHON_SUPPORT=ON .
# Make, this step takes a long time to run.
make
make install
# Create a new file with the content bellow (without #)
# /usr/local/lib 
nano /etc/ld.so.conf.d/opencv.conf
ldconfig

# Append next 2 lines to file bash.bashrc (without #)
# PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/local/lib/pkgconfig
# export PKG_CONFIG_PATH
gedit /etc/bash.bashrc
```

## Compiling C samples ##
```
cd /opt/OpenCV-2.3.0/samples/c
chmod +x build_all.sh
./build_all.sh
```

## Testing C samples ##
```
cd /opt/OpenCV-2.3.0/samples/c
./facedetect --cascade="/usr/local/share/opencv/haarcascades/haarcascade_frontalface_alt.xml" --scale=1.5 lena.jpg
./facedetect --cascade="/usr/local/share/opencv/haarcascades/haarcascade_frontalface_alt.xml" --scale=1.5
```

## Testing Python samples ##
```
# "OpenCV" is the OpenCV directory
cp "OpenCV"/data "OpenCV"/samples
# Testing
cd /opt/OpenCV-2.3.0/samples/python
./facedetect.py 0
./motempl.py (contorno e movimento)
./laplace.py (contorno)
```



---

```

```

**Read More:**

> _**OpenCV**_
```
  http://opencv.itseez.com/
  http://opencv.willowgarage.com/wiki/Welcome
  http://opencv.willowgarage.com/documentation/python/cookbook.html
  http://opencv.willowgarage.com/wiki/Android
  http://opencv.willowgarage.com/wiki/AndroidSamples
```