# Introduction #

This document explains how to install some Python libraries needed by the SOM4R.


# Details #

This installation guide was tested on Ubuntu 10.04 with Python 2.6.5 and PyUSB 1.0a0. It also can be used as a guideline to install these components on others Linux distributions using similar packages.

## Libraries Installation ##

Installing the libraries that is needed by the SOM4R Vehicle WS software.
Running scripts on Terminal window:
```
#root access
sudo -i
apt-get update

# Python
apt-get install python python-dev python-setuptools python-espeak libespeak-dev python-serial python-dev python-numpy 

# Web.Py
apt-get install python-webpy libapache2-mod-wsgi apache2-threaded-dev

# USB libraries
apt-get install libusb libusb-dev
```
Download pyusb-1.0.0-a0.tar.gz from (https://sourceforge.net/projects/pyusb/files/)
```
unzip ./pyusb-1.0.0-a0.tar.gz
cd ./pyusb-1.0.0-a0
python setup.py install
export PYTHONPATH="/usr/local/lib/python2.6/dist-packages:$PYTHONPATH"
```
Grant permission on USB port in file /etc/init.d/rc.local, adding the line bellow:
> sudo chmod 666 /dev/ttyUSB0

Test as root.


---

```

```

**Read More:**

> _**Web.Py**_
```
  http://webpy.org/
  http://webpy.org/cookbook
  http://webpy.org/docs/0.3/tutorial
  http://webpy.org/docs/0.3
  http://faruk.akgul.org/blog/entry/getting-started-with-webpy
  http://webpy.org/src
  http://webpy.org/recommended_setup
```
> _**PyUSB**_
```
  https://sourceforge.net/apps/mediawiki/pyusb/index.php?title=Main_Page
  http://pyusb.sourceforge.net/docs/1.0/tutorial.html
  https://sourceforge.net/apps/trac/libusb-win32/wiki
  http://bleyer.org/pyusb/
  http://www.beyondlogic.org/usbnutshell/usb5.htm
```
> _**HTTP Digest Authentication with Python and Php**_
```
  http://en.wikipedia.org/wiki/Digest_Access_Authentication
  http://oauth.net/2/
  http://webpy.org/cookbook/userauthbasic
  http://www.voidspace.org.uk/python/articles/authentication.shtml
  http://webpy.org/tutorial3
  http://securitytechscience.com/blog/?p=12
  http://docs.python.org/library/hashlib.html
  http://docs.python.org/library/urllib2.html
  http://docs.python.org/library/httplib.html
  http://www.faqs.org/rfcs/rfc2617.html
  http://old.blog.jimhoskins.com/?p=5
  http://old.blog.jimhoskins.com/?p=4
  http://www.tutorialspoint.com/python/python_dictionary.htm
  http://effbot.org/zone/python-list.htm
  http://www.peej.co.uk/projects/phphttpdigest
  http://www.rooftopsolutions.nl/blog/223
  http://shortrecipes.blogspot.com/2009/12/php-generation-of-md5-hash-for-http.html
  http://www.httpwatch.com/httpgallery/authentication/
```
> _**Apache Integration**_
```
  http://webpy.org/cookbook/mod_wsgi-apache
  http://wiki.web2py.com/web2py_and_mod_wsgi_apache_as_non_root
  http://octave.1599824.n4.nabble.com/PHP-help-td2264800.html
```
> _**Others**_
```
  http://stackoverflow.com/questions/713847/recommendations-of-python-rest-web-services-framework
  http://www.roseindia.net/jmeter/using-jmeter.shtml
  http://seanbehan.com/python/mod_python-and-web-py-on-ubuntu/
  http://www.linuxquestions.org/questions/slackware-14/wheres-etc-security-console-perms-333655/
  http://www.mail-archive.com/python-list@python.org/msg21378.html
  http://starship.python.net/crew/theller/ctypes/
  http://www.jython.org/
  http://wiki.python.org/jython/JythonBibliography
  http://www.portablepython.com/
```