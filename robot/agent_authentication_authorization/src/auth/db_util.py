# To change this template, choose Tools | Templates
# and open the template in the editor.


import MySQLdb
import time

import xml_util


def connect():
    # Conectando com o BD.
    db=MySQLdb.connect(
        host="localhost", port=3306, user="robot", passwd="123456", db="robot")
    return db


def persist_resource(db,id_source,resource_text):
    
    result=xml_util.dict_to_rdfxml(\
        {"rdfs:comment":"error in db_util.persist_resource."}\
        , id_source)
    
#    id_source=xml_util.key_attribute_from_xml(\
#        resource_text,"rdf:Description","rdf:ID")

    # gerando id
    id=int(time.time()*10000)
#    print type(id)
#    print "id "+ str(id)
    # Gravando no BD.
    cursor=db.cursor()
    # Prepare SQL query to INSERT a record into the database.
    sql="""INSERT INTO tbl_stm (id_resource, resource_text, id_source)
        VALUES ("""+str(id)+""", %s, %s)"""
#    print "SQL = " + sql
    try:
        # Execute the SQL command
        cursor.execute(sql,(resource_text,id_source))
        # Commit your changes in the database
        db.commit()
        result=xml_util.dict_to_rdfxml(\
            {"id_resource":id}\
            , "response")
    except:
        # Rollback in case there is any error
        db.rollback()
        print "error in db_util.persist_resource------------"
    
    return result