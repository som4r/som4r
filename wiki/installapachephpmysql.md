# Introduction #

This document explains how to install Apache, Php and Mysql on Ubuntu.


# Details #

This installation guide was tested on Ubuntu 10.10 with Apache httpd 2.0, Php 5.3.3 and Mysql 5. It also can be used as a guideline to install these components on others Linux distributions using similar packages.

## Libraries Installation ##

Installing the libraries that is needed by the Core of SOM4R and Human Machine Interface (HMI) software.
Running scripts on Terminal window:
```

#root access
sudo -i
apt-get update
  
# Apache 2
apt-get install apache2
  
# Php 5.3
apt-get install libapache2-mod-php5 php5-adodb php5-imagick php5-mcrypt php5-suhosin php5-cgi php5-cli php5-common php5-curl php5-gd php5-ldap php5-mysql php5-pgsql php5-sqlite php5-xmlrpc php5-xsl php5-sybase

```


### Php5 Configuration ###

```
nano /etc/php5/apache2/php.ini
```

Change this settings:

  * memory\_limit (128M default, 256M recommended)
  * post\_max\_size (8M default, 50M recommended)
  * upload\_max\_filesize (2M default, 50M recommended)

### Enabling mod\_rewrite ###
```
a2enmod rewrite
nano /etc/apache2/sites-available/default
```

Inside block: Directory /var/www/  change from: AllowOverride None  to: AllowOverride All


### Restart Apache Server ###
```
/etc/init.d/apache2 restart
```

### Php Instalation Test ###
```
mkdir -p /var/www/php
nano /var/www/php/index.php [ ?php phpinfo();? ]
```

Open an internet browser and point to:  http://localhost/php


### MySql e PhpMyAdmin ###

```
apt-get install mysql-server
```
You'll be promped for root password.

```
apt-get install phpmyadmin
```
  * Choose apache2
  * Configure with dbcommons? yes
  * Enter mysql root pasword
  * Define a phpmyadmin password (empty is recommended)


---

```

```


**Read More:**

> _**Apache httpd 2**_
```
  http://httpd.apache.org/
```
> _**Php**_
```
  http://php.net/
```
> _**Mysql**_
```
  http://www.mysql.com/
```
> _**Others**_
```
  http://ubuntu.5.x6.nabble.com/mod-rewrite-no-Ubuntu-11-04-td14037.html
```