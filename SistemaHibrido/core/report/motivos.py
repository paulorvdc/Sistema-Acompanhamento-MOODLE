from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from pymongo import MongoClient
import pandas as pd
import numpy as np

#não funcional nessa versão
def motivos_function(request, banco):
    all_entries = banco.rotulados.find({})
    data = pd.DataFrame(list(all_entries))
    if not('motivo' in data):
        messages.error(request, 'Não existem motivos de alunos desistentes, rotule pelo menos um desistente, para ter acesso!')
        return redirect('/canvas/model')
    else:
        data = data.fillna('')
        data = data[['id','motivo']]
        data = data[data['motivo'] != '']
        data = data.groupby(["motivo"])["id"].count()
        data = data.reset_index()
        print(data)
        context = {
            'motivos':data['id'].to_json(),
            'label':data['motivo'].to_json(),
        }
        return render(request, 'modelo/canvas_motivos.html', context)