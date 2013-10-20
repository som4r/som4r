#! /usr/bin/python

import urllib2


theurl='http://localhost:8012/authentication/'

authhandler=urllib2.HTTPDigestAuthHandler()
authhandler.add_password(realm="realm@som4r.net",
      uri=theurl,
      user="tts",
      passwd="123456")
opener=urllib2.build_opener(authhandler)
result=opener.open(theurl)
thepage=result.read()
#urllib2.install_opener(opener)
#req = urllib2.Request(theurl)
#res = urllib2.urlopen(req)
print thepage
#print "\nsecond call\n"
#result=opener.open(theurl)
#thepage=result.read()
#print thepage
