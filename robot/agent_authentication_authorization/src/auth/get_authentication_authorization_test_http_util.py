#! /usr/bin/python

import http_util
import xml_util


theurl='http://localhost:8080/authentication/'
host="localhost:8080"

token,xml_resource=http_util.http_authentication("realm@som4r.net"\
    ,host,"robot","123456")
print "\nauthentication"
print xml_resource
#token=xml_util.key_from_xml(xml_resource,"token")
print "token="+token
print "\nauthorization"
server_timeout,client_timeout,client_username\
    =http_util.http_authorization(host,token,token)
print str(server_timeout)+" : "+str(client_timeout)+" : "+client_username
