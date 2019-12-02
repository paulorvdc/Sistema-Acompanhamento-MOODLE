from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse

def start(request):
  user = request.user
  if user.is_authenticated:
    return redirect('home')
  else:
    return redirect('login')