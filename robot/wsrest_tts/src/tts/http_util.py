#!/usr/bin/env python

import httplib
import sys
import urllib2
import time

import xml_util
import global_data

global_data.valid_tokens={}

def http_request(method,host,page,headers=None,token=None,resource_rdfxml=None):

    # validando os parametros.
    if (isinstance(method,str) and method.upper() in ['GET','POST'] \
        and isinstance(host,str) and len(host)>0 \
        and isinstance(page,str) and len(page)>0 \
        and (isinstance(headers,dict) or headers is None) \
        and (isinstance(token,str) or token is None) \
        and (isinstance(resource_rdfxml,str) or resource_rdfxml is None)):
            
        headers={"Content-type": "application/xml; charset=utf-8"}\
            if headers is None or isinstance(headers,dict)==False else headers
        # inserindo token no header
        if isinstance(token,str) and len(token)>0:
            headers["authorization"]="token="+token
        try:
            conn=httplib.HTTPConnection(host)
            # GET
            if method=='get':
                conn.request("GET",page,None,headers)
            # POST
            elif method=='post':
                conn.request("POST",page,resource_rdfxml,headers)

            response=conn.getresponse()
            xml_response=response.read()
            conn.close()
        except:
            xml_response=xml_util.dict_to_rdfxml(\
                {"message":"http_"+str(method)+" "+str(host)+str(page)\
                ,"info":sys.exc_info()[0]}\
                ,"error")
            print xml_response
        return xml_response
    else:
        raise Exception


def http_authentication(realm,host,user,passwd):

#    theurl='http://localhost:8080/authentication/'
    # validando os parametros.
    if isinstance(realm,str) and len(realm)>0 \
        and isinstance(host,str) and len(host)>0 \
        and isinstance(user,str) and len(user)>0 \
        and isinstance(passwd,str) and len(passwd)>0:
        # certificando a presenca do http:// na variavel host
        if host[:7].upper()!="HTTP://":
            host="http://"+host
        host=host+"/authentication/"
        token=None
        try:
            # autenticando o usuario.
            authhandler=urllib2.HTTPDigestAuthHandler()
            authhandler.add_password(realm,host,user,passwd)
            opener=urllib2.build_opener(authhandler)
            result=opener.open(host)
            # recebendo o token, ou o erro de nao autorizado.
            xml_response=result.read()
            token=xml_util.key_parent_from_xml\
                (xml_response,"token","authentication")
            token_timeout_s=int(xml_util.key_parent_from_xml\
                (xml_response,"timeout_s","authentication"))
            # Gravando o token e timeout deste servico/agente. Vai usar na autorizacao interna.
            global_data.valid_tokens[token]=\
                user+":::"+str(token_timeout_s+int(time.time()))
        except:
            xml_response=xml_util.dict_to_rdfxml(\
                {"message":"http_authentication "+str(host)\
                ,"info":str(sys.exc_info()[0])}\
                ,"error")
            print xml_response
        return token,xml_response
    else:
        return "invalid_parameters"
#        raise Exception
    
def http_authorization(host,server_token,client_token):

    # validando os parametros.
    if isinstance(host,str) and len(host)>0 \
        and isinstance(server_token,str) and len(server_token)>0 \
        and isinstance(client_token,str) and len(client_token)>0:

        # seguranca desabilitada?
        if server_token=="anonymous" or client_token=="anonymous":
            return 1,1,"anonymous"
        
        # tokens jah autorizados. validacao interna (cache).
        now_s=int(time.time())
        try:
            user_timeout=global_data.valid_tokens[client_token].split(":::")
            client_username=user_timeout[0]
            client_timeout=max(0,int(user_timeout[1])-now_s)
            user_timeout=global_data.valid_tokens[server_token].split(":::")
            server_timeout=max(0,int(user_timeout[1])-now_s)
        except:
            server_timeout,client_timeout=0,0
        # tokens sao validos?   
        if server_timeout>0 and client_timeout>0:
#            print "ok ------------------- "+str(server_timeout)+" "+str(client_timeout)+" "+client_username
            return server_timeout,client_timeout,client_username

        # token nao existe no cache, validando no servidor de autorizacao.
        # removendo possivel htpp://
        if host[:7].upper()=="HTTP://":
            host=host[7:]
            
        token="token="+server_token+":"+client_token
        conn=httplib.HTTPConnection(host)
        headers={"Content-type": "application/xml; charset=utf-8",
            "authorization":token}
        conn.request("GET","/authorization/",None,headers)
        response=conn.getresponse()
        xml_resource=response.read()
        try:
            server_timeout=int(xml_util.key_parent_from_xml\
                (xml_resource,"server_timeout_s","authorization"))
            client_timeout=int(xml_util.key_parent_from_xml\
                (xml_resource,"client_timeout_s","authorization"))
            client_username=xml_util.key_parent_from_xml\
                (xml_resource,"client_username","authorization")
            if client_timeout>0 and len(client_username)>0:
                # Gravando o token e timeout do cliente. Vai usar na autorizacao interna.
                global_data.valid_tokens[client_token]=\
                    client_username+":::"+str(client_timeout+int(time.time()))
        except:
            server_timeout,client_timeout=0,0
            client_username=""
        return server_timeout,client_timeout,client_username
    else:
        return 0,0,"invalid_parameters"
#        raise Exception

def http_get_token_in_header(web):
    
    token=""
    try:
        auth=web.ctx.environ['HTTP_AUTHORIZATION'] 
        # or = web.ctx.env.get('HTTP_AUTHENTICATE')
        if auth is not None and isinstance(auth,str) and auth[:6]=="token=":
            token=auth[6:]
    #        print "TOKEN="+str(result)
    except:
        token="error in http_get_token_in_header"
    return token