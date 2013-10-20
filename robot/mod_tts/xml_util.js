/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

function array_to_rdfxml(resource_array,description_id) {
    
    var buffer=new StringBuffer();
    buffer.append("<?xml version='1.0' encoding='UTF-8'?>");
    buffer.append("<!DOCTYPE rdf:RDF");
    buffer.append( " [<!ENTITY xsd 'http://www.w3.org/2001/XMLSchema#'>]>");
    buffer.append("<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'");
    buffer.append(" xmlns:rdfs='http://www.w3.org/2000/01/rdf-schema#'");
//    buffer.append(" xmlns:dc='http://purl.org/dc/elements/1.1/'");
    buffer.append(">");
    buffer.append("<rdf:Description ");
    buffer.append("rdf:ID='"+description_id+"'>");

    buffer.append(array_to_xml(resource_array));

    buffer.append('</rdf:Description></rdf:RDF>');
    
    return buffer.toString();
}

function array_to_xml(resource_array) {

    var buf=new StringBuffer();
    for (i=0; i<resource_array.length; i++ )
    {
        var chave_valor=resource_array[i];
        if ((typeof chave_valor)=="array") {
            buf.append(array_to_xml(chave_valor));
        }
        else if ((typeof chave_valor)=="string" 
            || (typeof chave_valor)=="number") {
            var parts=chave_valor.split(":");
            buf.append("<"+parts[0]+">"+parts[1]+"</"+parts[0]+">");
        }
    }
    return buf.toString();
}

function StringBuffer() {
    this.__strings__ = new Array;
}

StringBuffer.prototype.append = function (str) {
    this.__strings__.push(str);
};

StringBuffer.prototype.toString = function () {
    return this.__strings__.join("");
};
