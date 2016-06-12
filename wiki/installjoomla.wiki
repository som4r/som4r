# Introduction #

This document explains how to install the Joomla CMS, used as the Human Machine Interface (HMI) of SOM4R.


# Details #

This installation guide was tested on Ubuntu 10.10 with Apache, Php 5.3.3-1, MySql and Joomla 1.5.20. It also can be used as a guideline to install these components on others Linux distributions using similar packages.

## Libraries Installation ##

Installing the libraries that is needed by the SOM4R MS-Kinect Sensor WS software.
Running scripts on Terminal window:
```
sudo -i
cd ~
# Download SOM4R HMI Backup from: (TODO: create link)
cd /var/www
mkdir portal
cd portal
unzip ~/SOM4R_HMI_BACKUP.zip
cd ..
chown nobody:root portal -R
/etc/init.d/apache2 restart
# Change parameter display_errors=off on file /etc/php5/apache2/php.ini
```

### Testing the Installation ###

Open an internet browser and point to: http://localhost/portal



---

```

```

**Read More:**

> _**Joomla Extensions:**_
```
  http://extensions.joomla.org/
```
> _**Others:**_
```
  http://www.akeebabackup.com/
```