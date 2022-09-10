from cgitb import html
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    text = 'Привет мир!'
    return HttpResponse(text)
