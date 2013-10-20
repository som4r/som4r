#!/usr/bin/env python

__author__="marcus"
__date__ ="$Jan 15, 2012 11:12:00 PM$"

import web
import hashlib
import time

import global_data
import xml_util
import db_util


urls=(
  "", "reload",
  "/(.*)", "index"
)

private_key="a1de320564fc36d4a712e927aa4e5b21"


class reload:
    def GET(self,none=None): raise web.seeother('/')
    def POST(self,none=None): raise web.seeother('/')

class index:

    # ========== Inicializacao unica por classe =================
    # Variaveis declaradas aqui sao usadas na classe usando self.
    
    # Conectando com o BD.
    db=db_util.connect()
    
    # ============ Final da Inicializacao unica por classe ======

    def GET(self,none=None):

        web.header('Content-Type', 'application/xml; charset=utf-8')
        
        # seguranca http digest estah desativada.
        if global_data.conf_http_digest==False:
            return xml_util.dict_to_rdfxml({"token":"anonymous"},'authentication')
        
        # somente acesso local estah ativado.
        if global_data.conf_only_localhost==True \
            and web.ctx.ip not in ["127.0.0.1","localhost"]: # TODO: ipv6 localhost?
            web.ctx.status = '401 Unauthorized'    
            return
        
        auth=web.ctx.env.get('HTTP_AUTHORIZATION')
#        print "auth"
#        print auth
        authreq=True
        if auth is not None:
            username=self.validate_http_authorization(auth)
#            print "username "+str(username)
            if username is not None:
                # gerando token
                token=hashlib.md5(str(int(time.time()*1000000))\
                    +private_key).hexdigest()
                resource={"token":token}
                resource["timeout_s"]=global_data.token_timeout_s
#                print "token="+token
                # resposta do servidor
                xml_resource=xml_util.dict_to_rdfxml(resource,'authentication')
                resource={"token":token}
                resource['ip']=web.ctx.ip
                resource['username']=username
#                resource['ip']=web.ctx.environ['REMOTE_ADDR']
#                print "resource "+str(resource)
                # Gravando token e username no servico STM.
                db_util.persist_resource(self.db\
                    ,"authentication"\
                    ,xml_util.dict_to_rdfxml(resource,'authentication'))
                # respondendo o token.
                return xml_resource
            
        if authreq:
            nonce_ts=str(int(time.time()*1000000))
            nonce=hashlib.md5(nonce_ts+": ETag :"+private_key).hexdigest()
#            print "nonce="+nonce
            global_data.valid_nonce[nonce_ts]=nonce
            param='Digest realm="'+global_data.realm+'",'\
                +'qop=auth,'\
                +'nonce="'+nonce+'",'\
                +'opaque="'+global_data.opaque+'"'
#            print "param="+param
            web.header('WWW-Authenticate',param)
            web.ctx.status='401 Unauthorized'
            return

    def POST(self, name):
        web.header('Content-Type', 'application/xml; charset=utf-8')
        web.ctx.status='401 Unauthorized'
        return
    
    def validate_http_authorization(self,auth):
        
        auth=auth[7:]   # removendo palavra Digest
        # colocando conteudo do header recebido num dict
        dict_param={'realm':'','qop':'','nonce':'','opaque':''\
            ,'nc':'','cnonce':'','username':'','uri':''}
        attributes=auth.split(',')
        for i in range(len(attributes)):
            # separando chave-valor
            list_temp=attributes[i].split('=')
#            print list_temp[0].strip()+"==="+list_temp[1]
            value_final=list_temp[1]
            if list_temp[1].find('"')==0:
                # removendo aspas duplas adicionais
                list_param=list_temp[1].split('"')
                value_final=list_param[1]
            dict_param[list_temp[0].strip()]=value_final
#            print list_temp[0].strip()
#            print value_final

        # removendo os nonce expirados (timeout 5s).
        now_ts=int(time.time())
        for nonce_ts in global_data.valid_nonce.keys():
            if now_ts-int(int(nonce_ts)/1000000)>5:
                del global_data.valid_nonce[nonce_ts]
        
        # TODO:limitando quantidade maxima de nonce
#        print "valid_nonce len = "+str(len(valid_nonce))
#        if len(valid_nonce)>100:
            
        # nonce eh valido?
        response=""
        match_response=False
        if dict_param['nonce'] in global_data.valid_nonce.values():
            
            # validando senha no BD (tbl_ltm).
            ha2=hashlib.md5("GET:"+dict_param['uri']).hexdigest()

            # Prepare SQL query HA1.
            sql="select resource_text from tbl_ltm where id_source='authentication'"
            self.db.query(sql)
            # result set
            rs=self.db.store_result()
            # loop (max=100)
            for row in rs.fetch_row(100):
                ha1=xml_util.key_parent_from_xml(row[0],'ha1','authentication') 
#                ha1=hashlib.md5("myuser:"+global_data.realm+":mypass").hexdigest()
#                ha2=hashlib.md5("GET:"+dict_param['uri']).hexdigest()
                username=xml_util.key_parent_from_xml\
                    (row[0],'username','authentication') 
                response=hashlib.md5(ha1+":"+dict_param['nonce']+":"+dict_param['nc']\
                    +':'+dict_param['cnonce']+":"+dict_param['qop']\
                    +":"+ha2).hexdigest()
                if response==dict_param['response'] \
                    and dict_param['username']==username:
                    # Found a match.
                    match_response=True
                    break
                
            # removendo nonce utilizado.
            list_values=global_data.valid_nonce.items()
            for i in range(len(list_values)):
                if list_values[i][1]==dict_param['nonce']:
                    del global_data.valid_nonce[list_values[i][0]]
        
        return dict_param['username'] if match_response else None


app_authentication=web.application(urls,locals())
