#! /usr/bin/python

import httplib

## Lendo servidor e passando o token.
#conn = httplib.HTTPConnection("localhost:8012")
#headers = {"Content-type": "application/xml; charset=utf-8",
#    "authorization":"token=a37b45ad793679ccb4bd85ef074744b5:d7d07db22409306d97ed6dedf7c23e47"}
#conn.request("GET", "/authorization/", None, headers)
#response = conn.getresponse()
#xml_response = response.read()
#print xml_response
#conn.close()


### testando get do servico tts
conn=httplib.HTTPConnection("localhost:8092")
headers={"Content-type":"application/xml; charset=utf-8",
    "authorization":"token=955f43336aa3807a269fe666a01dfed2"}
conn.request("POST", "/", \
    "<rdf:RDF><rdf:Description rdf:ID='tts'><text_to_speech>testando</text_to_speech></rdf:Description></rdf:RDF>"\
    , headers)
response=conn.getresponse()
xml_response=response.read()
print "xml_response "+xml_response
conn.close()

## testando get do servico gps
#conn=httplib.HTTPConnection("localhost:8080")
#headers={"Content-type":"application/xml; charset=utf-8",
#    "authenticate":"token=5706de8e399bcc74c83dac9d5af0130f"}
#conn.request("GET","/",None,headers)
#response=conn.getresponse()
#xml_response=response.read()
#print "xml_response "+xml_response
#conn.close()