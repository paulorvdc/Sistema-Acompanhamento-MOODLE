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
from unicodedata import normalize
from core.report.regras import nomear_classificacao
from core.report.regras import nomear_rotulo

def report_function(request, banco, course, datestart, datefinish, fullname):
  #todos os dados processados na collection são trazidos para serem utilizados na previsão do modelo
  collect = banco[course + "_" + datestart + "_" + datefinish]
  all_entries = collect.find({})
  df =  pd.DataFrame(list(all_entries))
  df = df.fillna(0)
  all_entries = banco.mdl_user.find({})
  users =  pd.DataFrame(list(all_entries))
  
  if 'rotular' in request.POST:
    if 'n_ativo' in request.POST:
      aluno = df[df['_id'] == int(request.POST['n_ativo'])]
      know_where = banco.historico_treino.find({'course':str(course)})
      know_where = pd.DataFrame(list(know_where))
      collect = banco["h" + str(know_where['conta'].iloc[0])]
      aluno = aluno.drop(columns={'rede'})
      aluno['rotulo'] = 0
      print(aluno)
      collect.save(aluno.to_dict('reports')[0])
      messages.success(request, "Aluno rotulado com sucesso!")
    else:
      aluno = df[df['_id'] == int(request.POST['ativo'])]
      know_where = banco.historico_treino.find({'course':str(course)})
      know_where = pd.DataFrame(list(know_where))
      collect = banco["h" + str(know_where['conta'].iloc[0])]
      aluno = aluno.drop(columns={'rede'})
      aluno['rotulo'] = 1
      collect.save(aluno.to_dict('reports')[0])
      messages.success(request, "Aluno rotulado com sucesso!")

  join = df.join(users.set_index("id"), on="_id", how='left', lsuffix='_left', rsuffix='_right')
  subset = join[['_id_left','firstname','lastname','rede']]
  subset = subset.rename(columns={'_id_left':'_id'})
  subset['rede'] = subset['rede'].apply(nomear_classificacao)
  subset['nome'] = subset['firstname'] + ' ' + subset['lastname']
  historico = banco.historico_treino.find({'course':str(course)})
  historico = pd.DataFrame(list(historico))
  rotulados = banco["h" + str(historico['conta'].iloc[0])]
  rotulos = rotulados.find({})
  rotulos = pd.DataFrame(list(rotulos))
  if rotulos.empty:
    subset = subset.rename(columns={'rede':'rotulo'})
    subset.rotulo = pd.Categorical(subset.rotulo, 
                          categories=["Alto Risco","Risco Intermediário","Sem Risco","Não Ativo","Ativo"],
                          ordered=True)
    subset = subset.sort_values(by=["rotulo","nome"])
  else:
    r_join = subset.join(rotulos.set_index("_id"), on="_id", how='left')
    r_join['rotulo'] = r_join['rotulo'].fillna(r_join['rede'])
    r_join['rotulo'] = r_join['rotulo'].apply(nomear_rotulo)
    
    subset = r_join[['_id','firstname','lastname','rotulo','nome']]
    subset = subset.rename(columns={'_id_left':'_id'})
    subset.rotulo = pd.Categorical(subset.rotulo, 
                          categories=["Alto Risco","Risco Intermediário","Sem Risco","Não Ativo","Ativo"],
                          ordered=True)
    subset = subset.sort_values(by=["rotulo","nome"])
  if request.POST:
    #apertar "Baixar CSV"
    if 'save' in request.POST:
      response = HttpResponse(content_type='text/csv')
      response['Content-Disposition'] = 'attachment; filename=situacao_alunos_' + normalize('NFKD',fullname).encode('ASCII','ignore').decode('ASCII') + '.csv'
      save = subset[['_id','nome','rotulo']]
      save.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
      return response
    #se houve pesquisa os dados são filtrados antes da exibição
    elif 'pesquisar' in request.POST:
      subset = subset[subset['nome'].str.match('.*' + request.POST['nome'], case=False)]
      subset = subset[subset['rotulo'].str.match('.*' + request.POST['classificacao'], case=False)]
      tuples = [tuple(x) for x in subset.values]
      data = ([x for x in tuples])
      return render(request, 'modelo/tabela.html', {'data':data, 'course':course, 'datestart':datestart, 'datefinish':datefinish, 'fullname':fullname})

  tuples = [tuple(x) for x in subset.values]
  data = ([x for x in tuples])
  return render(request, 'modelo/tabela.html', {'data':data, 'course':course, 'datestart':datestart, 'datefinish':datefinish, 'fullname':fullname})
