# Introduction #

This document explains how to install Media Server and Video Streaming softwares.


# Details #

This installation guide was tested on Ubuntu 11.04 with Red5 and ffmpeg. It also can be used as a guideline to install these components on others Linux distributions using similar packages.

## Libraries Installation - I ##

Installing the libraries that is needed by the SOM4R Landmark Detection WS software.
Running scripts on Terminal window:
```
# As root
sudo -i
apt-get update

# Java
apt-get install java-1.6.0-openjdk java-1.6.0-openjdk-devel
apt-get ant subversion ivy

# red5
mkdir ~/red5
svn co http://red5.googlecode.com/svn/java/server/tags/0_9_1 red5-0.9.1.svn
cd ~/red5/red5-0.9.1.svn
# Fixing bug of this version
# Visit http://trac.red5.org/attachment/ticket/693/red5-fix-ffmpeg-publish.diff
# and http://trac.red5.org/ticket/693
gedit cd ~/red5/red5-0.9.1.svn/src/org/red5/server/net/rtmp/codec/RTMPProtocolDecoder.java
# Next step takes about 10 minutes
ant clean dist 
# Install applications (e.g. oflaDemo) in this url:
http://localhost:5080/installer/
```

## Testing Red5 ##
```
cd ~/red5/red5-0.9.1.svn/dist
./red5.sh
```

Open this site:
> http://localhost:5800


## Libraries Installation - II ##
```
# Xuggler
cd ~/
mkdir xuggler
cd xuggler
git clone git://github.com/xuggle/xuggle-xuggler.git
export XUGGLE_HOME=/usr/local/xuggler
export PATH=$XUGGLE_HOME/bin:$PATH
export LD_LIBRARY_PATH=$XUGGLE_HOME/lib:$LD_LIBRARY_PATH
cd xuggler/xuggle-xuggler
# Next step takes about 86 min.
sudo ant run-tests
sudo ant install
```

## Testing FFmpeg ##

```
LD_LIBRARY_PATH=/usr/local/xuggler/lib

/usr/local/xuggler/bin/ffmpeg -f video4linux2 -s 800x600 -r 15 -i /dev/video0 -qscale 5 -f flv rtmp://127.0.0.1/oflaDemo/red5StreamDemo
```


## Testing rtmp Cient ##

Open this site

> http://localhost:5080/demos/simpleSubscriber.html

Testing local connection:

> rtmp://localhost/oflaDemo

Testing remote connection:

> rtmp://IP\_REMOTO:1935/oflaDemo
> or rtmp://IP\_REMOTO/oflaDemo


---

```

```

**Read More:**

> _**Red5 and Xuggler:**_
```
http://en.wikipedia.org/wiki/Real_Time_Messaging_Protocol
http://www.red5.org/
http://wiki.red5.org/wiki/Install
http://red5wiki.com/wiki/Live_streaming
http://www.xuggle.com/xuggler/build
```
> _**RTMP Clients**_
```
http://code.google.com/p/rtmplite/
http://www.rtmpy.org/index.html
http://code.google.com/p/sabreamf/wiki/FAQ
http://code.google.com/p/rtmpjs/
http://www.flashrealtime.com/rtmp-client-control-fms-remotely/
```
> _**Others**_
```
http://e.kesken.org/2009/07/what-i-learned-about-red5-rtmp-and.html
http://blog.flexexamples.com/tag/getcamera/
http://blog.flexexamples.com/2008/01/22/displaying-a-webcams-video-in-a-flex-videodisplay-control/
http://www.adobe.com/devnet/flex/articles/help_callcenter.html
```