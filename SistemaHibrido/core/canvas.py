import pandas as pd
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
import time
import datetime

from core.report.regras import dia_da_semana

#variáveis globais para uso com função de geração de proporção
size = 1
def proporcao(valor):
  global size
  if size == 0:
    size = 1
  return valor/size

def canvas_function(request, banco):
  if request.POST:
    #esse passo trata do último estágio de seleção de informações
    action = 'viewed'
    target = 'course'
    #aqui o usuário escolhe uma disciplina (precisa ser escolhida)
    if request.POST['course']=='':
      messages.error(request, 'Disciplina não selecionada!')
      return render(request, 'core/message.html')
    curso = int(request.POST['course'])
    #uma data de inicio e de fim (precisam ser escolhidas e não podem ser maiores que o dia atual)
    start = request.POST['datestart']
    finish = request.POST['datefinish']
    if start == '' or finish == '':
      messages.error(request, 'Datas de inicio e final não foram definidas corretamente!')
      return render(request, 'core/message.html')

    start = str(start)
    finish = str(finish)
    start = time.mktime(datetime.datetime.strptime(start, "%Y-%m-%d").timetuple())
    finish = time.mktime(datetime.datetime.strptime(finish, "%Y-%m-%d").timetuple())
    action = 'viewed'
    target = 'course'
    aluno = 5
    professor = 3
    tutor = 4
    
    pipeline = [
        #filtra a tabela para alunos com algumas das informações fixas e conseguidas anteriormente
        {
          "$match":{
            "$and":[{'action':action},{'courseid':curso},{'target':target},{'timecreated':{"$gt":start, "$lt":finish}}]
          }
        },
        #realiza um join do log com a tabela de roles
        {
        "$lookup":{
            "from": "mdl_role_assignments", 
            "localField": "userid",   
            "foreignField": "userid", 
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
        #filtra os dados restantes
        {
          "$match":{
            "$or":[{'roleid':aluno},{'roleid':professor},{'roleid':tutor}]
          }
        }
      ]
    data = banco.mdl_logstore_standard_log.aggregate(pipeline)    
    data = pd.DataFrame(list(data))
    #se nenhum dado for recuperado o usuário retorna a tela inicial de seleção
    if data.empty:
      messages.error(request, 'Essa disciplina não possuí interações nesse periodo de tempo!')
      return render(request, 'core/message.html')
    else:
      #filtragem de funcionários UAB
      nomes = banco.data_lake_nomes.find({})
      nomes = pd.DataFrame(list(nomes))
      data = nomes.join(data.set_index("userid"), on="id", how="inner", lsuffix="_left", rsuffix="_right")
      data = data[data['name'] != 'Graduação']
      data = data[data['name'] != 'Nead-TI']
      data = data[data['name'] != 'PEDAGOGICO']
      data = data[['id', 'firstname', 'lastname', 'category',
       'name', 'roleid_left','target', 'action', 'timecreated', 'courseid']]
      data = data.rename(columns={'roleid_left':'roleid', 'id':'userid'})
      #senão os dados são convertidos em dos tipos de exibição escolhidos
      if request.POST["exibicao"]=="dias":
        #aqui o campo de momento da ação é transformado em dias da semana
        data['timecreated'] = pd.to_datetime(data['timecreated'],unit='s')
        data['dia_semana'] = data.timecreated.dt.dayofweek
        data['dia_semana'] = data['dia_semana'].apply(dia_da_semana)
        data.dia_semana = pd.Categorical(data.dia_semana, 
                      categories=["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"],
                      ordered=True)
        data = data.sort_values(by="dia_semana")

        #os dados são separados entre alunos e professores
        data_aluno = data[data['roleid'] == 5]
        data_professor = data[data['roleid'] == 3]
        data_tutor = data[data['roleid'] == 4]

        #as quantidades de alunos e professores são armazenadas para futura utilização no gráfico de proporção
        alunos, professores, tutores = data_aluno['userid'].drop_duplicates().size, data_professor['userid'].drop_duplicates().size, data_tutor['userid'].drop_duplicates().size

        data_aluno = data_aluno.groupby(["dia_semana"])["action"].count()
        data_professor = data_professor.groupby(["dia_semana"])["action"].count()
        data_tutor = data_tutor.groupby(["dia_semana"])["action"].count()

        data_aluno  = data_aluno.reset_index()
        data_professor  = data_professor.reset_index()
        data_tutor  = data_tutor.reset_index()

      elif request.POST["exibicao"]=="horas":
        #aqui o campo de momento da ação é transformado na hora em que foi realizado
        data['timecreated'] = pd.to_datetime(data['timecreated'],unit='s')
        data['hora'] = data.timecreated.dt.hour
        data['hora'] = data['hora'].astype("category")
        data = data.sort_values(by="hora")
    
        data_aluno = data[data['roleid'] == 5]
        data_professor = data[data['roleid'] == 3]
        data_tutor = data[data['roleid'] == 4]

        alunos, professores, tutores = data_aluno['userid'].drop_duplicates().size, data_professor['userid'].drop_duplicates().size, data_tutor['userid'].drop_duplicates().size

        data_aluno = data_aluno.groupby(["hora"])["action"].count()
        data_professor = data_professor.groupby(["hora"])["action"].count()
        data_tutor = data_tutor.groupby(["hora"])["action"].count()

        data_aluno  = data_aluno.reset_index()
        data_professor  = data_professor.reset_index()
        data_tutor  = data_tutor.reset_index()
    
    estatisitica = ''
    if request.POST['estatistica'] == "proporcao":
      #se o gráfico desejado é o de proporção a quantidade de visualizações é dividida pela quantidade cadastrada na disciplina
      global size
      size = alunos
      data_aluno["action"] = data_aluno["action"].apply(proporcao) 
      size = professores
      data_professor["action"] = data_professor["action"].apply(proporcao) 
      size = tutores
      data_tutor["action"] = data_tutor["action"].apply(proporcao)
      estatisitica = "Proporção"
    else:
      estatisitica = "Contagem"
  
    #aqui é encontrado o nome da diciplina para exibir na interface
    disciplina = banco.mdl_course.find({'id':curso})
    disciplina = list(disciplina)
    #label é selecionado de acordo com tipo de exibição
    tipo = ''
    if request.POST["exibicao"]=="dias":
      label = data_aluno['dia_semana'].to_json()
      tipo = "Dias da Semana"
    else:
      label = data_aluno['hora'].to_json()
      tipo = "Horas do Dia"
    #dados necessários para a tela em si ou para permitir o retorno a telas anteriores
    context = {
      'data_aluno': data_aluno['action'].to_json(),
      'data_professor': data_professor['action'].to_json(),
      'data_tutor': data_tutor['action'].to_json(),
      'label': label,
      'disciplina':disciplina[0]['fullname'], 
      'tipo': tipo,
      'estatisitica':estatisitica
    }
    log = {'user':request.user.username, 'disciplina':disciplina[0]['fullname'], 'tipo': tipo, 'estatisitica':estatisitica, 'start':start, 'finish':finish, 'timegenerated':datetime.datetime.now()}
    banco.log_graficos.insert_one(log)
    if request.POST['tipo_grafico'] == "bar":
      return render(request, 'core/canvas_bar.html', context)
    else:
      return render(request, 'core/canvas_line.html', context)
  else:
    #consulta que isola as course_categories que abrigam cada tipo de curso
    all_entries = banco.mdl_course_categories.find({"$or":[{'id':14},{'id':17},{'id':18}]})
    df =  pd.DataFrame(list(all_entries))
    subset = df[['id', 'name']]
    tuples = [tuple(x) for x in subset.values]
    parents = ([x for x in tuples])
    return render(request, 'core/canvas.html', {'parents': parents})