# Introduction #

This document explains how to install the Speech Recognition Libraries and others prerequisites to run SOM4R Listen and TTS Web Services.


# Details #

This installation guide was tested on Ubuntu 10.10 with GStreamer 0.10, Pocketsphinx 0.7, Python 2.6.6 and python-espeak 0.1. It also was used as a guideline to install the libraries on Fedora 14 with similar packages.



## Libraries Installation ##


> We going to start installing the libraries that is needed by the SOM4R Listen WS software.

> On the Ubuntu 10.10 open Synaptic Package Manager.

```
  tool bar -> System -> Administration -> Add/Remove Software
```

> Search for the follow package collection and apply then:

  * **sphinxbase-pyton** Python interface to sphinxbase (sphinxbase-pyton-0.7-1.fc14)
  * **sphinxbase-libs** Libraries for sphinxbase (sphinxbase-libs-0.7-1.fc14(i686))
  * **sphinxbase-devel** Header and other development files for sphinxbase (sphinxbase-devel-0.7-1.fc14(i686))
  * **pocketsphinx-pyton** Python interface to pocketsphinx (pocketsphinx-pyton-0.7-1.fc14(i686))
  * **pocketsphinx-libs** Shared libraries for pocketsphinx executables (pocketsphinx-libs-0.7-1.fc14(i686))
  * **pocketsphinx-devel** Header files for developing with pocketsphinx (pocketsphinx-devel-0.7-1.fc14(i686))
  * **gstreamer-python** Python binding for GStreamer (gstreamer-python-0.10.19-1.fc14(i686))
  * **numpy** A fast multidimensional array facility for Python (numpy-1:1.4.1-6.fc14(i686))
  * **scipy** Scientific Tools for Python (scipy-0.7.2-2.fc14(i686)) -> this going to ask to intall the **f2py for numpy** -> (numpy-f2py-1:1.4.1-6.fc14(i686) <- too
  * **python-espeak**
  * **espeak**
  * **libespeak-dev**
  * **espeak-data**
  * **libjack0**


## Testing the Installation ##


> To test the speech recognition you have to:

  * Create a text file with the words that you want to recognize with the software, one word per line.

> (corpus.txt)
```
YES
NO
HI
ROBOT
VOICE
COMMAND
```


  * Accesses the LMTool website (http://www.speech.cs.cmu.edu/tools/lmtool.html), select your **_corpus.txt_** file and click on the "COMPILE KNOWLEDGE BASE" button.
  * Download the zip file (ex: 1234.zip) and extract to `  <LM_DIR> `, a local directory like ` /home/user/som4r/lm/ `.

  * Open a Terminal window to login like super user and run the following commands.

```
  su
  cd <LM_DIR>
  chmod +x *
  pocketsphinx_continuous -hmm /usr/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k -lm 1234.lm -dict 1234.dic
```
> ps: You can change the file names acording with the files that you downloaded on the lm tool website.

> As as result, the _PocketSphinx_ software will show the info data follows by the word **_"Ready"_** what means that the software is detecting the sounds around and a silence moment is find the word _**"Listening"**_ appears to  indicate that the software is analyzing the sounds and comparing with the words from _corpus.txt_ file.

> TODO: print screen

> Speak a word, when the software recognition is done it send the data information followed by the word that it recognized from the text file and will be back to the "Ready" status.

> TODO: print screen


## Testing the eSpeak Installation ##


Open a Terminal window and run the following command.
```
  espeak testing
```


---

```

```

**Read More:**

> _**Speech recognition in Linux:**_
```
  http://en.wikipedia.org/wiki/Speech_recognition_in_Linux
  http://www.voxforge.org/
```
> _**CMU Sphinx**_
```
  http://cmusphinx.sourceforge.net/
  http://cmusphinx.sourceforge.net/wiki/
  http://cmusphinx.sourceforge.net/wiki/gstreamer
  http://cmusphinx.sourceforge.net/wiki/installingpythonstuff
  http://cmusphinx.sourceforge.net/wiki/tutorialpocketsphinx?
  http://cmusphinx.sourceforge.net/wiki/tutoriallm
  http://cmusphinx.sourceforge.net/wiki/download#models
```
> _**Python GStreamer**_
```
  http://pygstdocs.berlios.de/pygst-tutorial/index.html
  http://www.jonobacon.org/2006/08/28/getting-started-with-gstreamer-with-python/
  http://achievewith.us/public/articles/2009/01/28/using-gstreamer-and-python-to-record-audio
```
> _**eSpeak**_
```
  http://espeak.sourceforge.net/
  http://espeak.sourceforge.net/speak_lib.h
  https://launchpad.net/python-espeak
  http://blog.rssat.net/content/siegfried-gevatter-introducing-espeak-gui
  https://answers.launchpad.net/python-espeak/+question/84380
  https://answers.launchpad.net/python-espeak/+question/65787
  http://comments.gmane.org/gmane.comp.audio.sox/3136
  http://www.digitalbuz.com/2009/11/03/solved-using-espeak-error-bt_audio_service_open-connect-failed-connection-refused-111/
```
> _**Others**_
```
  http://www.bigwebmaster.com/General/Howtos/Speech-Recognition-HOWTO/software.html#FREESOFTWARE
  http://nico.nikkostrom.com/
  http://www-03.ibm.com/software/products/us/en/worklight
  http://www.daniweb.com/software-development/python/threads/88358/python-for-laptop-robot-speech-recognition-and-tts
  http://bloc.eurion.net/archives/2008/writing-a-command-and-control-application-with-voice-recognition/
```