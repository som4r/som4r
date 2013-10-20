# To change this template, choose Tools | Templates
# and open the template in the editor.


import MySQLdb
import time


def connect():
    # Conectando com o BD.
    db = MySQLdb.connect(
        host="localhost", port=3306, user="robot", passwd="123456", db="robot")
    return db


def persist_resource(db, id_source, resource_text):
    cursor = db.cursor()
    # Prepare SQL query to INSERT a record into the database.
    sql = """INSERT INTO tbl_stm (id_resource, resource_text, id_source)
        VALUES (%d, "%s", "%s")""" \
        % (int(time.time() * 10000) \
        ,resource_text, id_source)
#        print "SQL = " + sql
    print
    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       db.rollback()

