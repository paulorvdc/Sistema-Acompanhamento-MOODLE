from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.externals import joblib
from datetime import datetime


def pipeline_curso_function(banco):

    pipeline = [
    {
        "$lookup":{
            "from": "mdl_enrol",       
            "localField": "enrolid",   
            "foreignField": "id", 
            "as": "total"         
         }
     },
     {
        "$replaceRoot": { "newRoot": { "$mergeObjects": [
            { "$arrayElemAt": [ "$total", 0 ] }, "$$ROOT" ] } }
       },
       
       { "$project": {
           "total": 0
            }
       },
       {
        "$lookup":{
            "from": "mdl_course",       
            "localField": "courseid",   
            "foreignField": "id", 
            "as": "total1"         
         }
     },
     
     {
           "$replaceRoot": { "newRoot": { "$mergeObjects": [
            { "$arrayElemAt": [ "$total1", 0 ] }, "$$ROOT" ] } }
       },
       
       { "$project": {
           "total1": 0
            }
       },
       {
        "$lookup":{
            "from": "mdl_course_categories",       
            "localField": "category",   
            "foreignField": "id", 
            "as": "total2"         
         }
     },
     
     {
           "$replaceRoot": { "newRoot": { "$mergeObjects": [
            { "$arrayElemAt": [ "$total2", 0 ] }, "$$ROOT" ] } }
       },
       
       { "$project": {
           "total2": 0
            }
       }
    ]
    all_entries = banco.mdl_user_enrolments.aggregate(pipeline)
    df =  pd.DataFrame(list(all_entries))
    df = df.fillna(0)
    return df