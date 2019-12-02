import mysql.connector
import pandas as pd
from pymongo import MongoClient
import json

cnx = mysql.connector.connect(user='phpmyadmin', password='36771488',
                              host='127.0.0.1',
                              database='nead')

client = MongoClient('localhost', 27017)
banco = client.SistemaHibrido

cursor = cnx.cursor()
query = ("SELECT * FROM mdl_course_categories")

data = pd.read_sql(query, con=cnx)

records = json.loads(data.T.to_json()).values()
#banco.mdl_course_categories.insert(records)

cursor = banco.mdl_course_categories.find({})
df =  pd.DataFrame(list(a))

subset = df[['id','name']]
tuples = [tuple(x) for x in subset.values]

[x for x in tuples]