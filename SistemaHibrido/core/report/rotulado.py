from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from pymongo import MongoClient
import pandas as pd
import numpy as np
from datetime import datetime

from core.report.regras import nomear_rotulo

#acoplado na tabela principal para essa versão
def rotulado_function(request, banco):
  all_entries = banco.rotulados.find({})
  df =  pd.DataFrame(list(all_entries))
  if df.empty:
        messages.error(request, 'Não existem rótulos de alunos, rotule pelo menos um aluno, para ter acesso!')
        return redirect('/canvas/model')
  else:
    df = df.fillna(0)
    subset = df[['id','regra']]
    all_entries = banco.mdl_user.find({})
    users =  pd.DataFrame(list(all_entries))
    join = subset.join(users.set_index("id"), on="id", how='inner')
    join = join.reset_index()
    if join.empty:
        messages.error(request, 'Não existem rótulos de alunos, rotule pelo menos um aluno, para ter acesso!')
        return redirect('/canvas/model')
    else:
        subset = join[['id','firstname','lastname','regra']]
        subset = subset.drop_duplicates()
        print(subset)
        subset['regra'] = subset['regra'].apply(nomear_rotulo)
        subset['nome'] = subset['firstname'] + ' ' + subset['lastname']
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
        join = subset.join(df.set_index("userid"), on="id", lsuffix='_left', rsuffix='_right')
        if join.empty:
            messages.error(request, 'Não existem rótulos de alunos, rotule pelo menos um aluno, para ter acesso!')
            return redirect('/canvas/model')
        else:
            subset = join[['nome','name','regra','id']]
            subset = subset.drop_duplicates()
            subset = subset[subset['name'] != 'Graduação']
            subset = subset[subset['name'] != 'Nead-TI']
            subset = subset[subset['name'] != 'PEDAGOGICO']
            subset = subset.sort_values(by=["name","nome","regra"])
            if request.POST:
                #apertar "Baixar CSV"
                if request.POST['save'] == '1':
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename=rotulos_alunos'+ str(datetime.now()) +'.csv'
                    subset.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
                    return response
                #se houve pesquisa os dados são filtrados antes da exibição
                if request.POST['deletar'] == '1':
                    banco.rotulados.remove({"id":int(request.POST['rotulado'])})
                    banco.processado.update({"_id":int(request.POST['rotulado'])}, {"$set": {"rotulado": 0} })
                    subset = subset[subset['id'] != int(request.POST['rotulado'])]
                    tuples = [tuple(x) for x in subset.values]
                    data = ([x for x in tuples])
                    return render(request, 'modelo/tabela_rotulados.html', {'data':data})
                else:
                    subset = subset[subset['nome'].str.match('.*' + request.POST['nome'], case=False)]
                    subset = subset[subset['name'].str.match('.*' + request.POST['curso'], case=False)]
                    subset = subset[subset['regra'].str.match('.*' + request.POST['rotulo'], case=False)]
                    tuples = [tuple(x) for x in subset.values]
                    data = ([x for x in tuples])
                    return render(request, 'modelo/tabela_rotulados.html', {'data':data})

            tuples = [tuple(x) for x in subset.values]
            data = ([x for x in tuples])
            return render(request, 'modelo/tabela_rotulados.html', {'data':data})