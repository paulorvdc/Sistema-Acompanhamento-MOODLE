from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import (REDIRECT_FIELD_NAME, get_user_model, login as auth_login)
from pymongo import MongoClient
import datetime
from core.mongo_config import MongoConfig

#conexão com o banco do mongo 
client =  MongoClient(username=MongoConfig.usuario, password=MongoConfig.senha, authSource=MongoConfig.source_auth)
#banco de dados com o nome chamado precisa estar criado
banco = client.SistemaHibrido

def register(request):
    if request.user.is_authenticated:
        l = []
        for g in request.user.groups.all():
            l.append(g.name)
        if 'admin' in l:
            if request.method=="POST":
                form = UserRegisterForm(request.POST)
                if form.is_valid():
                    user = form.save()
                    
                    if request.POST['tipo'] =='isAdm':
                        check = 1
                        log = {'user':request.user.username, 'target':user.username, 'isAdm':True, 'action':'create', 'timegenerated':datetime.datetime.now()}
                        banco.log_users.insert_one(log)
                    
                    elif request.POST['tipo'] =='isCor':
                        check = 2
                        log = {'user':request.user.username, 'target':user.username, 'isCor':True, 'action':'create', 'timegenerated':datetime.datetime.now()}
                        banco.log_users.insert_one(log)

                    else:
                        check = False
                        log = {'user':request.user.username, 'target':user.username, 'isAdm':False, 'action':'create', 'timegenerated':datetime.datetime.now()}
                        banco.log_users.insert_one(log)

                    if check == 1:
                        group = Group.objects.get(name='admin')
                        user.groups.add(group)
                        group = Group.objects.get(name='coordenador')
                        user.groups.add(group)
                    elif check == 2:
                        group = Group.objects.get(name='coordenador')
                        print(group)
                        group.user_set.add(user)
                        print(user.groups.all())
                    username = form.cleaned_data.get('username')
                    messages.success(request, 'Conta criada para {}!'.format(username))
                    return redirect('home')
            else:
                form = UserRegisterForm()
            return render(request, 'users/register.html',{'form':form})
        else:
            return redirect('home')
    else:
        return redirect('login')

def delete(request):
    if request.user.is_authenticated:
        l = []
        for g in request.user.groups.all():
            l.append(g.name)
        if 'admin' in l:
            if request.method=="POST":
                print(request.POST)
                username = request.POST["editar"]
                try:
                    u = User.objects.get(username = username)
                    if u.username != request.user.username:
                        log = {'user':request.user.username, 'target':u.username, 'action':'delete', 'timegenerated':datetime.datetime.now()}
                        banco.log_users.insert_one(log)
                        u.delete()
                        messages.success(request, "Usuário Deletado")
                    else:
                        log = {'user':request.user.username, 'action':'tried_suicide', 'timegenerated':datetime.datetime.now()}
                        banco.log_users.insert_one(log)
                        messages.error(request, "Tentou se deletar")

    
                except u.DoesNotExist:
                    messages.error(request, "Usuario não existe")    
                return redirect("home")
        
            else:
                all_entries = User.objects.all()
                context = {
                    'data': all_entries
                }
                return render(request, 'users/edit.html',context)
        else:
            return redirect('home')
    else:
        return redirect('login')

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect('home')
        else:
            messages.error(request,'Usuário ou senha incorretos')
            return redirect('login')

    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})
