from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from pymongo import MongoClient
import pandas as pd
import numpy as np
import time
import datetime
import os


def acompanhamento_function(request,banco):
    if request.POST:
        if request.POST['category']=='':
            messages.error(request, 'Curso não selecionado corretamente!')
            return render(request, 'core/message.html')
        else:
            category = int(request.POST['category'])
            entries = banco.mdl_course.find({'category':category})
            df2 = pd.DataFrame(list(entries))

            if df2.empty:
                messages.error(request, 'Curso sem disciplinas processadas')
                return render(request, 'core/message.html')

            df2 = df2[['id', 'fullname']]
            entries = banco.mdl_course_categories.find({'id':int(request.POST['category'])})
            curso = pd.DataFrame(list(entries))
            curso = curso['name'].drop_duplicates().iloc[0]
    
            all_entries = banco.historico_treino.find({})
            df =  pd.DataFrame(list(all_entries))
            df = df.fillna(0)

            if df.empty:
                messages.error(request, 'Sem dados para essa disciplina')
                return render(request, 'core/message.html')

            df["course"] = df["course"].astype(int)

            join = df.join(df2.set_index("id"), on="course", how='left')
            join = join [['course','datestart','datefinish','fullname']]
            join = join.fillna('sem')
            join = join[join['fullname']!='sem']
            join = join.reset_index()
            print(join)
            if join.empty:
                messages.error(request, 'Curso sem histórico')
                return render(request, 'core/message.html')
            join['datestart'] = pd.to_datetime(join['datestart'],unit='s')
            join['datestart'] = join['datestart'].apply(lambda x: x.strftime('%Y-%m-%d'))
            join['datefinish'] = pd.to_datetime(join['datefinish'],unit='s')
            join['datefinish'] = join['datefinish'].apply(lambda x: x.strftime('%Y-%m-%d'))

            #contagem de previsões disciplina a disciplina
            lista = []
            for i in range(len(join['course'])):
                collect = banco[str(join['course'][i]) + "_" + join['datestart'][i] + "_" + join['datefinish'][i]]
                datefinish = join['datefinish'][i]
                all_entries = collect.find({})
                df =  pd.DataFrame(list(all_entries))
                df = df.fillna(0)
                resultado = df['rede'].value_counts().reset_index()
                print(resultado)
                if resultado[resultado['index'] == 2].empty:
                    sem = 0
                else:
                    sem = resultado['rede'][resultado['index'] == 2].iloc[0]
                if resultado[resultado['index'] == 1].empty:
                    inter = 0
                else:
                    inter = resultado['rede'][resultado['index'] == 1].iloc[0]
                if resultado[resultado['index'] == 0].empty:
                    alto = 0
                else:
                    alto = resultado['rede'][resultado['index'] == 0].iloc[0]
                dicio = {'sem':sem, 'inter':inter, 'alto':alto, 'data':datefinish}
                lista.append(dicio)
            
            new_df = pd.DataFrame(lista)
            context = {
            'sem': new_df['sem'].to_json(),
            'inter': new_df['inter'].to_json(),
            'alto': new_df['alto'].to_json(),
            'label': new_df['data'].to_json(),
            'curso': curso
            }
            print(context)
            print(new_df)
            return render(request, 'core/canvas_line_acompanhamento.html', context)
    #consulta que isola as course_categories que abrigam cada tipo de curso
    all_entries = banco.mdl_course_categories.find({"$or":[{'id':14},{'id':17},{'id':18}]})
    df =  pd.DataFrame(list(all_entries))
    subset = df[['id', 'name']]
    tuples = [tuple(x) for x in subset.values]
    parents = ([x for x in tuples])
    return render(request, 'modelo/acompanhamento.html', {'parents': parents})