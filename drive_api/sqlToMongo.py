#!/home/mineracao/documentos/Sistema-hibrido-com-interface/alan/SistemaHibrido/env/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 10:08:31 2019

@author: pauloricardo
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient 

host_mysql = '<host mysql>'
database_mysql = '<database mysql>'
user_mysql = '<user mysql>'
password_mysql = '<senha mysql>'

try: 
    #se mongodb precisar de autenticação e for local, senao consultar documentacao para conexão
    conn = MongoClient(username="<user mongodb>",password="<senha mongodb>", authSource="admin") #authSource provavelmente será admin, senao alterar
    print("Connected successfully!!!") 
except:   
    print("Could not connect to MongoDB")
#Nome do banco de dados no MongoDB 
db = conn.<nome database mongodb>

#course_categories
try:
    connection = mysql.connector.connect(host=host_mysql,
                             database=database_mysql,
                             user=user_mysql,
                             password=password_mysql)
    if connection.is_connected():
       cursor = connection.cursor()
       cursor.execute("SELECT id,name,parent FROM mdl_course_categories")
       record = cursor.fetchall()       
except Error as e :
    print ("Error while connecting to MySQL", e)
finally:
    if(connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

course_categories = pd.DataFrame(record)
course_categories.columns = ['id','name','parent']  
  
#trecho padrão para cada tabela
collection = db.mdl_course_categories
collection.drop()

records = collection.insert_many(course_categories.to_dict('records'))

#user
try:
    connection = mysql.connector.connect(host=host_mysql,
                             database=database_mysql,
                             user=user_mysql,
                             password=password_mysql)
    if connection.is_connected():
       cursor = connection.cursor()
       cursor.execute("SELECT id,firstname,lastname,lastaccess FROM mdl_user")
       record = cursor.fetchall()       
except Error as e :
    print ("Error while connecting to MySQL", e)
finally:
    if(connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

user = pd.DataFrame(record)
user.columns = ['id','firstname','lastname','lastaccess']
  
#trecho padrão para cada tabela  
collection = db.mdl_user
collection.drop()

records = collection.insert_many(user.to_dict('records'))

#log
try:
    connection = mysql.connector.connect(host=host_mysql,
                             database=database_mysql,
                             user=user_mysql,
                             password=password_mysql)
    if connection.is_connected():
       cursor = connection.cursor()
       cursor.execute("SELECT target,action,timecreated,userid,courseid FROM mdl_logstore_standard_log")
       record = cursor.fetchall()       
except Error as e :
    print ("Error while connecting to MySQL", e)
finally:
    if(connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

course = pd.DataFrame(record)
course.columns = ["target","action","timecreated","userid","courseid"]
  
#trecho padrão para cada tabela  
collection = db.mdl_logstore_standard_log
collection.drop()

records = collection.insert_many(course.to_dict('records'))

#role_assignments
try:
    connection = mysql.connector.connect(host=host_mysql,
                             database=database_mysql,
                             user=user_mysql,
                             password=password_mysql)
    if connection.is_connected():
       cursor = connection.cursor()
       cursor.execute("SELECT id,userid,roleid FROM mdl_role_assignments")
       record = cursor.fetchall()       
except Error as e :
    print ("Error while connecting to MySQL", e)
finally:
    if(connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

role_assignments = pd.DataFrame(record)
role_assignments.columns = ['id','userid','roleid']
  
#trecho padrão para cada tabela  
collection = db.mdl_role_assignments
collection.drop()

records = collection.insert_many(role_assignments.to_dict('records'))

#data_lake
try:
    connection = mysql.connector.connect(host=host_mysql,
                             database=database_mysql,
                             user=user_mysql,
                             password=password_mysql)
    if connection.is_connected():
       cursor = connection.cursor()
       cursor.execute("SELECT DISTINCT ue.id,ue.userid,ue.enrolid,e.courseid,l.action,l.target,l.timecreated,r.roleid FROM mdl_user_enrolments ue JOIN mdl_enrol e ON e.id=ue.enrolid JOIN mdl_logstore_standard_log l ON l.userid=ue.userid JOIN mdl_role_assignments r ON r.userid=ue.userid")
       record = cursor.fetchall()       
except Error as e :
    print ("Error while connecting to MySQL", e)
finally:
    if(connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

data_lake = pd.DataFrame(record)
data_lake.columns = ['id','userid','enrolid','courseid','action','target','timecreated','roleid']
  
#trecho padrão para cada tabela  
collection = db.data_lake
collection.drop()

records = collection.insert_many(data_lake.to_dict('records'))

#course
try:
    connection = mysql.connector.connect(host=host_mysql,
                             database=database_mysql,
                             user=user_mysql,
                             password=password_mysql)
    if connection.is_connected():
       cursor = connection.cursor()
       cursor.execute("SELECT id,fullname,category FROM mdl_course")
       record = cursor.fetchall()       
except Error as e :
    print ("Error while connecting to MySQL", e)
finally:
    if(connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

course = pd.DataFrame(record)
course.columns = ['id','fullname','category']
  
#trecho padrão para cada tabela
collection = db.mdl_course
collection.drop()

records = collection.insert_many(course.to_dict('records'))

#datalake para nomes
try:
    connection = mysql.connector.connect(host=host_mysql,
                             database=database_mysql,
                             user=user_mysql,
                             password=password_mysql)
    if connection.is_connected():
       cursor = connection.cursor()
       cursor.execute("SELECT DISTINCT u.id,u.firstname,u.lastname,c.category,cc.name,ra.roleid FROM mdl_user u JOIN mdl_user_enrolments ue ON ue.userid=u.id JOIN mdl_enrol e ON e.id=ue.enrolid JOIN mdl_course c ON c.id=e.courseid JOIN mdl_course_categories cc ON cc.id=c.category JOIN mdl_role_assignments ra ON ra.userid=u.id")
       record = cursor.fetchall()       
except Error as e :
    print ("Error while connecting to MySQL", e)
finally:
    if(connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

course = pd.DataFrame(record)
course.columns = ['id','firstname','lastname','category','name','roleid']
  
#trecho padrão para cada tabela  
collection = db.data_lake_nomes
collection.drop()

records = collection.insert_many(course.to_dict('records'))
