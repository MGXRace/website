from django.shortcuts import render
from django.views.generic import View

__author__ = 'Mark'


class NotFound(View):
    def get(self, request):
        return render(request, 'racesow/error.html')

    def post(self, request):
        return render(request, 'racesow/error.html')