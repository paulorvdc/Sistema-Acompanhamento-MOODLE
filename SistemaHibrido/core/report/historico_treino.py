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

from core.report.regras import nomear_classificacao
from core.report.report import report_function

def historico_function(request, banco):
  #todos os dados pré-processados na collection são trazidos para serem utilizados na previsão do modelo
  all_entries = banco.historico_treino.find({})
  historico =  pd.DataFrame(list(all_entries)) #dataframe com o historico de todas as previsoes
  if historico.empty:
    messages.error(request, 'Não há processamentos prontos no sistema!')
    return redirect('home')
  historico = historico.fillna(0)
  
   #*********************************************************************#
  all_entries = banco.mdl_course.find({})
  disciplina =  pd.DataFrame(list(all_entries)) #dataframe com todas as disciplinas
  disciplina = disciplina.fillna(0)
  historico["course"] = historico["course"].astype(int)
  join = historico.join(disciplina.set_index("id"), on="course", how='left', lsuffix='_left', rsuffix='_right')
  join = join [['course','datestart','datefinish','fullname','category']]

  #*********************************************************************#
  all_entries = banco.mdl_course_categories.find({})
  curso =  pd.DataFrame(list(all_entries)) #Data frame com todos os cursos
  curso = curso.fillna(0)
  join = join.join(curso.set_index("id"), on="category", how='left')
  join = join [['course','datestart','datefinish','fullname','category','name']]
  join['datestart'] = pd.to_datetime(join['datestart'],unit='s')
  join['datestart'] = join['datestart'].apply(lambda x: x.strftime('%Y-%m-%d'))
  join['datefinish'] = pd.to_datetime(join['datefinish'],unit='s')
  join['datefinish'] = join['datefinish'].apply(lambda x: x.strftime('%Y-%m-%d'))

   #*********************************************************************#
  if request.POST:
    #se pesquisa por nome
    if 'pesquisar_historico' in request.POST:
      join = join[join['fullname'].str.match('.*' + request.POST['nome'], case=False)]
      join = join[join['name'].str.match('.*' + request.POST['curso'], case=False)]
      join = join[join['datestart'].str.match('.*' + request.POST['inicial'], case=False)]
      join = join[join['datefinish'].str.match('.*' + request.POST['final'], case=False)]
      tuples = [tuple(x) for x in join.values]
      data = ([x for x in tuples])
      return render(request, 'modelo/tabela_historico.html', {'data':data})
    #se deletar todo o processamento e referencias a ele
    elif 'deletar' in request.POST:
      collect = banco[request.POST['course'] + "_" + request.POST['datestart'] + "_" + request.POST['datefinish']]
      collect.drop()
      banco.historico_treino.remove({'course':request.POST['course']})
      messages.success(request, 'Processamento deletado com sucesso!')
      return redirect('model')
    else:
      #se visualizar o resultado individual de cada processamento
      return report_function(request, banco, request.POST['course'], request.POST['datestart'],request.POST['datefinish'], request.POST['fullname'])
  else:
    tuples = [tuple(x) for x in join.values]
    data = ([x for x in tuples])
    return render(request, 'modelo/tabela_historico.html', {'data':data})