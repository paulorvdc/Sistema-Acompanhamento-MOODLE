from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import joblib
import os
from datetime import datetime
from core.report.rede_neural import criar_primeira_rede
from core.report.regras import saida_rede
from core.report.regras import create_rotulo
from core.report.regras import numerar_rotulo
from core.report.regras import nomear_classificacao
from core.report.regras import nomear_rotulo
from core.report.pre_mongodb import pre_processamento
import csv
from io import StringIO
from django.core.mail import EmailMessage
from django.contrib.auth.models import User


def processado_function(banco,course,datestart,datefinish,PROJECT_PATH,request):
    if banco.historico_treino.find({'course':str(course)}).count() > 0:
        messages.error(request, 'Disciplina já processada pelo sistema, se quiser processa-la em outro período delete o existente!')
        return redirect('home')
    else:
        #pré processamento e contagem para alunos, data e período de tempo
        banco.intermediaria_processado.insert_many(list(banco.data_lake.find({'roleid':5, 'courseid':course, 'timecreated':{"$gt":datestart, "$lt":datefinish}})))
            
        #consultas a serem realizadas no banco do mongodb
        pre_processamento(banco)

        #prepara os dados criando colunas, caso elas não existam
        all_entries = banco.processado.find({})
        df =  pd.DataFrame(list(all_entries))
        df = df.fillna(0)
        target_list = ['Created_Discussion_Subscription', 'Created_Post', 'Created_Submission',
        'Total_Action', 'Total_Created', 'Total_Viewed', 'Viewed_Attempt',
        'Viewed_Course', 'Viewed_Course_Module', 'Viewed_Discussion',
        'Viewed_Grade_Report', 'Viewed_Message', 'Viewed_Submission_Form',
        'Viewed_Submission_Status']
        df = df.reindex(sorted(df.columns), axis=1)
        if len(df.columns) < 16:
                l = [x for x in target_list if x not in df.columns]
                for i in range(len(l)):
                    df[l[i]] = 0
        df = df.reindex(sorted(df.columns), axis=1)
        
        #inicio da passagem pelo kmeans para obter a conta utilizada
        X = df.drop(columns={'_id'})
        kmeans = KMeans(n_clusters=5, init='k-means++', max_iter=3000)
        kmeans.fit(X)
        clusters = kmeans.cluster_centers_
        #conta a partir do cluster
        clusters = pd.DataFrame(clusters)
        contas = pd.DataFrame([{"mean":clusters.mean().mean(),"max":clusters.max().max(),"min":clusters[clusters != 0].min().min()}])
        conta = contas.sum(axis=1) / X['Total_Action'].count()
        conta = conta.iloc[0]

        #verifica se existem redes treinadas no sistema
        all_entries = banco.historico_redes.find({})
        redes = pd.DataFrame(list(all_entries))
        if redes.empty:
            opcoes = pd.DataFrame()
        #se existirem redes e verificado se esta pode ser utilizada
        #para que possa ser utilizada o resultado da conta precisa estar dentro de uma margem de 5 de diferença com a rede treinada
        else:
            opcoes = redes['contas'][redes[["contas"]].apply(np.isclose, b=conta, atol=5).any(1)]

        import keras
        from keras.utils.np_utils import to_categorical
        from keras import backend as K 

        if opcoes.empty:
            #sem opcão de rede ou de tabela de rotulos
            print('Rede nova')
            K.clear_session()
            #encontra todos os alunos cadastrados nesse curso, independete do acesso no período
            users = banco.data_lake.find({'action':'viewed','target':'course','roleid':5, 'courseid':course})
            users = pd.DataFrame(list(users))
            #cria o rotulo de acesso no período
            users['acao'] = users['timecreated'].apply(create_rotulo, datestart=datestart, datefinish=datefinish)
            users = users.groupby(['userid'])['acao'].sum().reset_index()
            users['rotulo'] = users['acao'].apply(numerar_rotulo)
            #junta alunos cadastrados que não acessaram com os que acessaram
            j_users = users.join(df.set_index("_id"), on="userid", how='left')
            #dados limpos para a rede
            X = j_users.fillna(0).drop(columns={'userid','acao','rotulo'})
            y = j_users['rotulo']
            classifier = criar_primeira_rede(X,y)
            #retira o predict pos treino
            j_users['rede'] = classifier.predict(X)
            j_users['rede'] = j_users['rede'].apply(saida_rede)
            course = str(course)
            historico = {
            'course': course,
            'datestart': datestart,
            'datefinish': datefinish,
            'conta':conta
            }
            datestart = pd.to_datetime(datestart,unit='s')
            datestart = datestart.strftime('%Y-%m-%d')
            datefinish = pd.to_datetime(datefinish,unit='s')
            datefinish = datefinish.strftime('%Y-%m-%d')
            collect = banco[course + "_" + datestart + "_" + datefinish]
            
            #salva os dados para acesso do treinamento na tabela ponteiro
            banco.historico_treino.insert_one(historico)
            j_users = j_users.drop(columns={'acao','rotulo'})
            j_users = j_users.rename(columns={'userid':'_id'})

            #salva os dados do treinamento na tabela endereçada
            collect.insert_many(j_users.to_dict('records'))
            #salva o treinamento da rede
            joblib.dump(classifier, PROJECT_PATH + "/models/rede" + str(conta) + ".sav")
            banco.historico_redes.insert_one({'contas':conta})
            messages.success(request, 'Dados processados com sucesso!')

            #enviar mensagem
            collect = banco[course + "_" + datestart + "_" + datefinish]
            all_entries = collect.find({})
            df =  pd.DataFrame(list(all_entries))
            df = df.fillna(0)
            all_entries = banco.mdl_user.find({})
            users =  pd.DataFrame(list(all_entries))

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
            
            admin = User.objects.filter(groups__name='admin')
            coordenador = User.objects.filter(groups__name='coordenador')
            email = []
            email2 = []
            for i in range(len(admin)):
                email.append(admin[i].email)
            for j in range(len(coordenador)):
                email2.append(coordenador[j].email)
            
            email_final = email+email2
            email = EmailMessage('Relatorio-alunos', 'relatorio dos alunos', 'suporte@nead.unicentro.br',
            bcc=email_final)

            all_entries = banco.historico_treino.find({'course':course})
            df =  pd.DataFrame(list(all_entries))
            df = df.fillna(0)

            all_entries = banco.mdl_course.find({})
            df2 =  pd.DataFrame(list(all_entries))
            df2 = df2.fillna(0)
            df["course"] = df["course"].astype(int)
            join = df.join(df2.set_index("id"), on="course", how='left', lsuffix='_left', rsuffix='_right')
            join = join [['course','datestart','datefinish','fullname','category']]

            all_entries = banco.mdl_course_categories.find({})
            df3 =  pd.DataFrame(list(all_entries))
            df3 = df3.fillna(0)
            join = join.join(df3.set_index("id"), on="category", how='left')
            join = join [['course','datestart','datefinish','fullname','category','name']]
            join['datestart'] = pd.to_datetime(join['datestart'],unit='s')
            join['datestart'] = join['datestart'].apply(lambda x: x.strftime('%Y-%m-%d'))
            join['datefinish'] = pd.to_datetime(join['datefinish'],unit='s')
            join['datefinish'] = join['datefinish'].apply(lambda x: x.strftime('%Y-%m-%d'))

            subset = subset[["nome","rotulo"]]
            subset.to_csv('relatorio.csv')
            data = []
            attachment_csv_file = StringIO()
            writer = csv.writer(attachment_csv_file)
            with open('relatorio.csv', 'r') as f:
                f_csv = csv.reader(f)
                # header = next(f_csv)
                for row in f_csv:
                    data.append(row)
            for i in range(int(len(data))):
                writer.writerow(data[i])
            email.attach('relatorio_'+ join['name'].iloc[0] + '_' + join['fullname'].iloc[0] + '.csv', attachment_csv_file.getvalue(),'text/csv')
            email.send(fail_silently=False)
        else:
            #com opcão de rede para ser usada
            print('Rede usada')
            
            opcao = opcoes.iloc[0]
            collect = banco["h" + str(opcao)]
            rotulado = collect.find({})
            rotulado = pd.DataFrame(list(rotulado))
            
            if rotulado.empty or df.join(rotulado.set_index("_id"), on="_id", how='inner', lsuffix='_left', rsuffix='_right').empty:
                #sem tabela de rotulado para o treinamento
                #realiza processo de busca de todos os usuários cadastrados no curso
                users = banco.data_lake.find({'action':'viewed','target':'course','roleid':5, 'courseid':course})
                users = pd.DataFrame(list(users))
                #cria o rotulo para o periodo para todos os alunos
                users['acao'] = users['timecreated'].apply(create_rotulo, datestart=datestart, datefinish=datefinish)
                users = users.groupby(['userid'])['acao'].sum().reset_index()
                users['rotulo'] = users['acao'].apply(numerar_rotulo)

                #prepara os dados da rede
                j_users = users.join(df.set_index("_id"), on="userid", how='left')
                X = j_users.fillna(0).drop(columns={'userid','acao','rotulo'})
                y = j_users['rotulo']
                
                K.clear_session()
                #carrega a rede selecionada para uso
                ann = joblib.load(PROJECT_PATH + "/models/rede" + str(opcao) + ".sav")
                #re-treina com um contingente menor de passadas
                ann.fit(X,y, batch_size = 10, epochs=200)
                #prediz o resultado
                j_users['rede'] = ann.predict(X)
                j_users['rede'] = j_users['rede'].apply(saida_rede)
                course = str(course)
                historico = {
                'course': course,
                'datestart': datestart,
                'datefinish': datefinish,
                'conta':opcao
                }
                datestart = pd.to_datetime(datestart,unit='s')
                datestart = datestart.strftime('%Y-%m-%d')
                datefinish = pd.to_datetime(datefinish,unit='s')
                datefinish = datefinish.strftime('%Y-%m-%d')
                collect = banco[course + "_" + datestart + "_" + datefinish]
                #salva os dados de direcionamento na tabela ponteiro
                banco.historico_treino.insert_one(historico)
                j_users = j_users.drop(columns={'acao','rotulo'})
                j_users = j_users.rename(columns={'userid':'_id'})
                #salva os dados do treinamento na tabela endereçada
                collect.insert_many(j_users.to_dict('records'))
                #salva o treinamento da rede
                joblib.dump(ann, PROJECT_PATH + "/models/rede" + str(opcao) + ".sav")
                messages.success(request, 'Dados processados com sucesso!')
                #enviar mensagem
                collect = banco[course + "_" + datestart + "_" + datefinish]
                all_entries = collect.find({})
                df =  pd.DataFrame(list(all_entries))
                df = df.fillna(0)
                all_entries = banco.mdl_user.find({})
                users =  pd.DataFrame(list(all_entries))

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
                
                admin = User.objects.filter(groups__name='admin')
                coordenador = User.objects.filter(groups__name='coordenador')
                email = []
                email2 = []
                for i in range(len(admin)):
                    email.append(admin[i].email)
                for j in range(len(coordenador)):
                    email2.append(coordenador[j].email)
                
                email_final = email+email2
                email = EmailMessage('Relatorio-alunos', 'relatorio dos alunos', 'suporte@nead.unicentro.br',
                bcc=email_final)

                all_entries = banco.historico_treino.find({'course':course})
                df =  pd.DataFrame(list(all_entries))
                df = df.fillna(0)

                all_entries = banco.mdl_course.find({})
                df2 =  pd.DataFrame(list(all_entries))
                df2 = df2.fillna(0)
                df["course"] = df["course"].astype(int)
                join = df.join(df2.set_index("id"), on="course", how='left', lsuffix='_left', rsuffix='_right')
                join = join [['course','datestart','datefinish','fullname','category']]

                all_entries = banco.mdl_course_categories.find({})
                df3 =  pd.DataFrame(list(all_entries))
                df3 = df3.fillna(0)
                join = join.join(df3.set_index("id"), on="category", how='left')
                join = join [['course','datestart','datefinish','fullname','category','name']]
                join['datestart'] = pd.to_datetime(join['datestart'],unit='s')
                join['datestart'] = join['datestart'].apply(lambda x: x.strftime('%Y-%m-%d'))
                join['datefinish'] = pd.to_datetime(join['datefinish'],unit='s')
                join['datefinish'] = join['datefinish'].apply(lambda x: x.strftime('%Y-%m-%d'))

                subset = subset[["nome","rotulo"]]
                subset.to_csv('relatorio.csv')
                data = []
                attachment_csv_file = StringIO()
                writer = csv.writer(attachment_csv_file)
                with open('relatorio.csv', 'r') as f:
                    f_csv = csv.reader(f)
                    # header = next(f_csv)
                    for row in f_csv:
                        data.append(row)
                for i in range(int(len(data))):
                    writer.writerow(data[i])
                email.attach('relatorio_'+ join['name'].iloc[0] + '_' + join['fullname'].iloc[0] + '.csv', attachment_csv_file.getvalue(),'text/csv')
                email.send(fail_silently=False)
            else:
                #com rede usada e tabela de rotulados para treinamento
                r_users = df.join(rotulado.set_index("_id"), on="_id", how='left', lsuffix='_left', rsuffix='_right')
                #pesquisa usuários do curso no banco
                users = banco.data_lake.find({'action':'viewed','target':'course','roleid':5, 'courseid':course})
                users = pd.DataFrame(list(users))
                users['acao'] = users['timecreated'].apply(create_rotulo, datestart=datestart, datefinish=datefinish)
                users = users.groupby(['userid'])['acao'].sum().reset_index()
                #gera semi rotulo com o acesso naquele periodo
                users['semi_rotulo'] = users['acao'].apply(numerar_rotulo)
                
                #realiza a junção de todos os alunos com aqueles que ja foram rotulados
                j_users = users.join(r_users.set_index("_id_left"), on="userid", how='left', lsuffix='_left', rsuffix='_right')
                j_users = j_users[['userid', 'semi_rotulo',
                                'Created_Discussion_Subscription_left', 'Created_Post_left',
                                'Created_Submission_left', 'Total_Action_left', 'Total_Created_left',
                                'Total_Viewed_left', 'Viewed_Attempt_left', 'Viewed_Course_left',
                                'Viewed_Course_Module_left', 'Viewed_Discussion_left',
                                'Viewed_Grade_Report_left', 'Viewed_Message_left',
                                'Viewed_Submission_Form_left', 'Viewed_Submission_Status_left', 'rotulo']]
                #alunos que não possuirem rotulo receberam o padrão gerado previamente
                j_users['rotulo'] = j_users['rotulo'].fillna(j_users['semi_rotulo'])
                j_users = j_users.rename(columns=['userid', 'semi_rotulo', 'Created_Discussion_Subscription', 'Created_Post',
                                'Created_Submission', 'Total_Action', 'Total_Created', 'Total_Viewed', 'Viewed_Attempt', 
                                'Viewed_Course', 'Viewed_Course_Module', 'Viewed_Discussion', 'Viewed_Grade_Report', 
                                'Viewed_Message', 'Viewed_Submission_Form', 'Viewed_Submission_Status', 'rotulo'])
                
                X = j_users.fillna(0).drop(columns={'userid','semi_rotulo','rotulo'})
                y = j_users['rotulo']

                K.clear_session()
                #carrega a rede selecionada
                ann = joblib.load(PROJECT_PATH + "/models/rede" + str(opcao) + ".sav")
                #re-treina com um contingente menor de passadas
                ann.fit(X,y, batch_size = 10, epochs=200)
                #gera a predição dessa disciplina
                j_users['rede'] = ann.predict(X)
                j_users['rede'] = j_users['rede'].apply(saida_rede)
                
                course = str(course)
                historico = {
                'course': course,
                'datestart': datestart,
                'datefinish': datefinish,
                'conta':opcao
                }
                datestart = pd.to_datetime(datestart,unit='s')
                datestart = datestart.strftime('%Y-%m-%d')
                datefinish = pd.to_datetime(datefinish,unit='s')
                datefinish = datefinish.strftime('%Y-%m-%d')
                collect = banco[course + "_" + datestart + "_" + datefinish]
                #salva os dados de endereçamento na tabela ponteiro
                banco.historico_treino.insert_one(historico)
                j_users = j_users.drop(columns={'semi_rotulo','rotulo'})
                j_users = j_users.rename(columns={'userid':'_id'})
                #salva os dados do treinamento na tabela endereçada
                collect.insert_many(j_users.to_dict('records'))
                #salva o treinamento da rede
                joblib.dump(ann, PROJECT_PATH + "/models/rede" + str(opcao) + ".sav")
                messages.success(request, 'Dados processados com sucesso!')
                #enviar mensagem
                collect = banco[course + "_" + datestart + "_" + datefinish]
                all_entries = collect.find({})
                df =  pd.DataFrame(list(all_entries))
                df = df.fillna(0)
                all_entries = banco.mdl_user.find({})
                users =  pd.DataFrame(list(all_entries))

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
                
                admin = User.objects.filter(groups__name='admin')
                coordenador = User.objects.filter(groups__name='coordenador')
                email = []
                email2 = []
                for i in range(len(admin)):
                    email.append(admin[i].email)
                for j in range(len(coordenador)):
                    email2.append(coordenador[j].email)
                
                email_final = email+email2
                email = EmailMessage('Relatorio-alunos', 'relatorio dos alunos', 'suporte@nead.unicentro.br',
                bcc=email_final)

                all_entries = banco.historico_treino.find({'course':course})
                df =  pd.DataFrame(list(all_entries))
                df = df.fillna(0)

                all_entries = banco.mdl_course.find({})
                df2 =  pd.DataFrame(list(all_entries))
                df2 = df2.fillna(0)
                df["course"] = df["course"].astype(int)
                join = df.join(df2.set_index("id"), on="course", how='left', lsuffix='_left', rsuffix='_right')
                join = join [['course','datestart','datefinish','fullname','category']]

                all_entries = banco.mdl_course_categories.find({})
                df3 =  pd.DataFrame(list(all_entries))
                df3 = df3.fillna(0)
                join = join.join(df3.set_index("id"), on="category", how='left')
                join = join [['course','datestart','datefinish','fullname','category','name']]
                join['datestart'] = pd.to_datetime(join['datestart'],unit='s')
                join['datestart'] = join['datestart'].apply(lambda x: x.strftime('%Y-%m-%d'))
                join['datefinish'] = pd.to_datetime(join['datefinish'],unit='s')
                join['datefinish'] = join['datefinish'].apply(lambda x: x.strftime('%Y-%m-%d'))

                subset = subset[["nome","rotulo"]]
                subset.to_csv('relatorio.csv')
                data = []
                attachment_csv_file = StringIO()
                writer = csv.writer(attachment_csv_file)
                with open('relatorio.csv', 'r') as f:
                    f_csv = csv.reader(f)
                    # header = next(f_csv)
                    for row in f_csv:
                        data.append(row)
                for i in range(int(len(data))):
                    writer.writerow(data[i])
                email.attach('relatorio_'+ join['name'].iloc[0] + '_' + join['fullname'].iloc[0] + '.csv', attachment_csv_file.getvalue(),'text/csv')
                email.send(fail_silently=False)
