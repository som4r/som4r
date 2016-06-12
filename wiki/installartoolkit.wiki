# Introduction #

This document explains how to install the ARToolKit libraries to run SOM4R Landmark Detection Web Service.


# Details #

This installation guide was tested on Ubuntu 10.04 with ARToolKit 2.72.1 and GStreamer. It also can be used as a guideline to install these components on others Linux distributions using similar packages.

## Libraries Installation ##

Installing the libraries that is needed by the SOM4R Landmark Detection WS software.
Running scripts on Terminal window:
```
# As root
sudo -i
apt-get update

# ARToolKit
wget http://downloads.sourceforge.net/project/artoolkit/artoolkit/2.72.1/ARToolKit-2.72.1.tgz
tar -zxvf ARToolKit-2.72.1.tgz
apt-get install freeglut3-dev libxmu-dev libxmu6 libxi6 libxi-dev

# GStreamer
apt-get install gstreamer-tools gstreamer0.10-tools gstreamer0.10-x libgstreamer0.10-0 libgstreamer0.10-dev python-gst0.10 python-gst0.10-dev python-gst0.10-rtsp gstreamer0.10-ffmpeg

# Configuration
cd ./ARToolKit
./Configure
```

Answers of questions:

> Color conversion should use x86 assembly (choose 'n' for 64bit systems)?

> Enter : n

> Do you want to create debug symbols? (y or n)

> Enter : n

> Build gsub libraries with texture rectangle support? (y or n) GL\_NV\_texture\_rectangle is supported on most NVidia graphics cards and on ATi Radeon and better graphics cards.

> Enter : y

```

# Compiling ARToolKit and examples
make

# Configuring environment
# GSTreamer
export ARTOOLKIT_CONFIG="v4l2src device=/dev/video??? use-fixed-fps=false ! ffmpegcolorspace ! capsfilter caps=video/x-raw-rgb,bpp=24 ! identity name=artoolkit ! fakesink"

# Testing examples
cd ./bin
./videoTest
./simpleTest
./exview (câmera)
./optical
./collideTest (Distance)

```



---

```

```

**Read More:**

> _**ARToolKit:**_
```
http://www.hitl.washington.edu/artoolkit/
http://en.wikipedia.org/wiki/ARToolKit
```
> _**Others:**_
```
http://www.ckirner.com/sacra
http://174.123.53.162/artigo/ARToolKit-Criando-aplicativos-de-Realidade-Aumentada/?pagina=2
http://ojs.pythonpapers.org/index.php/tppm/article/view/95/95
http://www.ckirner.com/realidadevirtual/?REALIDADE_AUMENTADA
http://forums.nvidia.com/index.php?showtopic=87692
http://openartisthq.org/debian/lucid/
```