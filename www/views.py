# -*- encoding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import Http404

from www.models import Page, Rubric, News

def error(request):
    '''
    Ошибка 404
    '''
    return render_to_response('www/404.html', {})
