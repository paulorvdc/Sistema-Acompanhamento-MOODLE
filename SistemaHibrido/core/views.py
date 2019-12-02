from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.externals import joblib
import time
import datetime
import os

from core.canvas import canvas_function
from core.report.historico_treino import historico_function
from core.report.acompanhamento import acompanhamento_function
from core.report.processado import processado_function
from core.report.rotulado import rotulado_function
from core.report.motivos import motivos_function
from django.contrib.auth.decorators import login_required
from core.mongo_config import MongoConfig

#utilização da biblioteca para criar caminhos de arquivos dentro do projeto dinamicamente
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

#conexão com o banco do mongo 
client =  MongoClient(username=MongoConfig.usuario, password=MongoConfig.senha,authSource=MongoConfig.source_auth)
#banco de dados com o nome chamado precisa estar criado
banco = client.SistemaHibrido

def home(request):
  user = request.user
  if user.is_authenticated:
    count_graficos = banco.log_graficos.find({}).count()
    count_reports = banco.historico_treino.find({}).count()
    
    count_ativ = 0
    count_n_ativ = 0
    rotulos = banco.historico_redes.find({})
    rotulos = pd.DataFrame(list(rotulos))
    if rotulos.empty:
      pass
    else:
      for i in range(rotulos['contas'].size):
        rotulados = banco["h" + str(rotulos['contas'].iloc[i])]
        count_ativ += rotulados.find({"rotulo":1}).count()
        count_n_ativ += rotulados.find({"rotulo":0}).count()

    return render(request, 'core/home.html', {'cgraphs':count_graficos, 'creports':count_reports, 'cativ':count_ativ, 'cnativ':count_n_ativ})
  else:
    return redirect('login')

def canvas(request):
  user = request.user
  if user.is_authenticated:
    return canvas_function(request, banco)
  else:
    return redirect('login')

def report(request):
  user = request.user
  if user.is_authenticated:
    return historico_function(request,banco)
  else:
    return redirect('login')

def rotulados(request):
  user = request.user
  if user.is_authenticated:
    return rotulado_function(request, banco)
  else:
    return redirect('login')

def motivos(request):
  user = request.user
  if user.is_authenticated:  
    return motivos_function(request, banco)
  else:
    return redirect('login')

def selecionar(request):
  user = request.user
  if user.is_authenticated:
    if request.POST:
      if request.POST['course'] == '':
        messages.error(request, 'Disciplina não selecionada corretamente!')
      else:
        course = int(request.POST['course'])
        datestart = request.POST['datestart']
        datefinish = request.POST['datefinish']
        if datestart != '' and datefinish != '':
          datestart = pd.to_datetime(datestart)
          datefinish = pd.to_datetime(datefinish)
          datestart = datestart.value//10 ** 9
          datefinish = datefinish.value//10 ** 9
          processado_function(banco,course,datestart,datefinish,PROJECT_PATH,request)
        else:
          messages.error(request, 'Data de inicio ou final não válida!')
      return redirect('selecionar')
    #consulta que isola as course_categories que abrigam cada tipo de curso
    all_entries = banco.mdl_course_categories.find({"$or":[{'id':14},{'id':17},{'id':18}]})
    df =  pd.DataFrame(list(all_entries))
    subset = df[['id', 'name']]
    tuples = [tuple(x) for x in subset.values]
    parents = ([x for x in tuples])
    return render(request, 'modelo/selecao.html', {'parents': parents})
  else:
    return redirect('login')

def load_categories(request):
  user = request.user
  if user.is_authenticated:
    parent = request.GET.get('parent')
    entries = banco.mdl_course_categories.find({'parent':int(parent)})
    df = pd.DataFrame(list(entries))
    subset = df[['id', 'name']]
    tuples = [tuple(x) for x in subset.values]
    categories = ([x for x in tuples])
    return render(request, 'modelo/load_categories.html', {'categories': categories})
  else:
    return redirect('login')

def load_courses(request):
  user = request.user
  if user.is_authenticated:
    category = request.GET.get('category')
    entries = banco.mdl_course.find({'category':int(category)})
    df = pd.DataFrame(list(entries))
    subset = df[['id', 'fullname']]
    tuples = [tuple(x) for x in subset.values]
    courses = ([x for x in tuples])
    return render(request, 'modelo/load_courses.html', {'courses': courses})
  else:
    return redirect('login')

def acompanhar(request):
  user = request.user
  if user.is_authenticated:
    return acompanhamento_function(request,banco)
  else:
    return redirect('login')
