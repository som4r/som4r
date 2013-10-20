# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="marcus"
__date__ ="$Oct 15, 2011 4:10:06 PM$"

import StringIO

def xml_to_dict(xml, resource):
    # ToDo: Usar api xml do python.
    # ToDo: Remover tudo que nao estiver dentro da tag do recurso
    # Criando copia do recurso global com o parametro xml.
    resource1 = resource.copy()
    # Procura pelos itens do recurso, ignorando os outros dados do xml.
    for item in resource1.items():
        key, value = item
        # Ignorando atributos: status
#            if key != 'status':
        inicio = xml.find("<" + key + ">")
        if inicio >= 0:
            final = xml.find("</" + key + ">")
            if inicio >= 0 and final > inicio:
                stringXml = xml[inicio + len(key) + 2 : final]
                if len(stringXml) > 0: # Ignorando chaves vazias.
                    # Tipo do recurso (string, float ou int)
                    if isinstance(resource1[key], int):
                        resource1[key] = int(stringXml)
                    if isinstance(resource1[key], float):
                        resource1[key] = float(stringXml)
                    else:   #String (default)
                        resource1[key] = str(stringXml)

#                        web.debug("key:value = " + key + " : " + str(resource1[key]))
    return resource1

def dict_to_rdfxml(resource, description_id):
    """ Transform a dict into a XML, writing to a stream """
    stream = StringIO.StringIO()
    stream.write("<?xml version='1.0' encoding='UTF-8'?>")
    stream.write("<!DOCTYPE rdf:RDF")
    stream.write( " [<!ENTITY xsd 'http://www.w3.org/2001/XMLSchema#'>]>")
    stream.write("<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'")
    stream.write(" xmlns:rdfs='http://www.w3.org/2000/01/rdf-schema#'")
#    stream.write(" xmlns:dc='http://purl.org/dc/elements/1.1/'")
    stream.write(">")
    stream.write("<rdf:Description ")
    stream.write("rdf:ID='%s'>" % description_id)

    stream.write(dict_to_xml(resource))

    stream.write('</rdf:Description></rdf:RDF>')
    stream.seek(0)
    return stream.read()

def dict_to_xml(resource):
    """ Transform a dict into a XML, writing to a stream """
    stream = StringIO.StringIO()
    for item in resource.items():
        key, value = item
        if isinstance(value, dict):
            stream.write('<%s>%s</%s>' % (key, \
                dict_to_xml(value), key))
        elif isinstance(value, str) \
            or isinstance(value, unicode):
            stream.write('<%s>%s</%s>' % (key, value, key))
        elif isinstance(value, int) \
            or isinstance(value, float) \
            or isinstance(value, long):
            stream.write('<%s>%d</%s>' % (key, value, key))
        else:
            stream.write(' unknown type')

    stream.seek(0)
    return stream.read()

def key_parent_from_xml(xml, key, description_id):
    result = ""
    # procurando descricao rdf.
    result0 = key_from_xml(xml, "rdf:Description")
#    print "parent key = " + result0
    if len(result0) > 0:
        # procurando id rdf.
        if result0.find("rdf:ID='" + description_id + "'") >= 0 \
            or result0.find('rdf:ID="' + description_id + '"') >= 0:
            # conteudo da chave.
            result = key_from_xml(result0, key)
#            print "key = " + result
    return result

def key_from_xml(xml, key):
    result = ""
    string_tests = [("<" + key + ">"), ("<" + key + " ")]
    for i in range(len(string_tests)):
        inicio = xml.find(string_tests[i])
        if inicio >= 0:
            final = xml.find("</" + key + ">")
            if inicio >= 0 and final > inicio:
                result = xml[inicio + len(key) + 2 : final]

    return str(result)  # forcando retorno string

def description_from_rdfxml(xml, description_id):
    result = ""
    # procurando descricao rdf.
    result0 = key_from_xml(xml, "rdf:Description")
    if len(result0) > 0:
        # procurando id rdf.
        if result0.find("rdf:ID='" + description_id + "'") >= 0 \
            or result0.find('rdf:ID="' + description_id + '"') >= 0:
            # conteudo completo da descricao.
            inicio = xml.find("<rdf:Description ")
            if inicio >= 0:
                final = xml.find("</rdf:Description>")
                if inicio >= 0 and final > inicio:
                    result = xml[inicio : final + len("</rdf:Description>")]
    return result

def key_attribute_from_xml(xml, key, attribute):
    result=""
    # procurando chave.
    string_tests = [("<" + key + ">"), ("<" + key + " ")]
    for i in range(len(string_tests)):
        inicio = xml.find(string_tests[i])
        if inicio >= 0:
            final = xml.find("</" + key + ">")
            if inicio >= 0 and final > inicio:
                result = xml[inicio : final+len(key)+3]
                break
    atributo=""
    if len(result) > 0:
        # procurando id rdf.
        inicio = result.find(attribute+"=")
        if inicio>=0:
            # conteudo do atributo.
            j=inicio+len(attribute)+1
            while (result[j]!=" " and result[j]!=">"):
                atributo=atributo+result[j]
                j=j+1
    if len(atributo)>0:
            if atributo[0]=="'" or atributo[0]=='"':
                atributo=atributo[1:len(atributo)-1]
    return atributo


#if __name__ == "__main__":
#
#    a = dict_to_rdfxml({"chave":"valor"},"idteste")
#    print a
#    b = description_from_rdfxml(a,"idteste")
#    print b