# Introduction #

This document explains how to install the OpenKinect libraries to run SOM4R MS-Kinect Sensor Web Service software.


# Details #

This installation guide was tested on Ubuntu 10.10 with libfreenect.  It also can be used as a guideline to install these components on others Linux distributions using similar packages.

## Libraries Installation ##

Installing the libraries that is needed by the SOM4R MS-Kinect Sensor WS software.
Running scripts on Terminal window:
```


sudo add-apt-repository ppa:arne-alamut/freenect
# If you are installing on Ubuntu 11.04, change the repository to Maverick (sinaptic repositories).
sudo apt-get update
sudo apt-get install freenect libfreenect
# Grant permission on "video" group
sudo adduser YOURUSERNAME video
# Next step take a long time to finish (zzz)
sudo easy_install cython
sudo apt-get install ipython
sudo apt-get install git-core cmake libglut3-dev pkg-config build-essential libxmu-dev libxi-dev libusb-1.0-0-dev libgtk2.0-dev pkg-config
cd ~/python_test
git clone https://github.com/OpenKinect/libfreenect.git
cd libfreenect
mkdir build
cd build
cmake ..
make
sudo make install
?https://github.com/amiller/libfreenect-goodies/blob/master/README.markdown
sudo ldconfig /usr/local/lib64/
```

### Installing Python Modules ###
```
cd ~/python_test/libfreenect/wrappers/python
sudo python setup.py install
```
Log-out Linux, disconnect and connect Kinect Sensor, and log-in again.

### Testing the Installation ###

```
freenect-glview
```

### Testing using Python Example ###
```
~/python_test/libfreenect/wrappers/python/demo_cv_async.py
```

### Testing within Python ###

```
python
  import freenect
  depth, timestamp = freenect.sync_get_depth()
```



---

```

```

**Read More:**

> _**Installation:**_
```
  http://openkinect.org/wiki/Getting_Started#Please_read_this_before_you_start
```
> _**Videos:**_
```
http://www.youtube.com/watch?v=Wic-_yK4Wz4&NR=1
http://www.youtube.com/watch?v=qwp1DqQt6yI
http://www.youtube.com/watch?v=uaci4dcZxYE
http://www.youtube.com/watch?v=2Gp3E7IwLRQ&NR=1&feature=fvwp
http://www.youtube.com/watch?v=FP1OVnZMUwo
http://www.youtube.com/watch?v=EFLo1cPNQi4&feature=related
```
> _**Others:**_
```
  http://download.oracle.com/javase/tutorial/security/index.html
  http://en.wikipedia.org/wiki/Sandbox_(computer_security)
  http://thetechjournal.com/how-to/how-to-hack-kinect.xhtml
  http://en.wikipedia.org/wiki/RANSAC
```