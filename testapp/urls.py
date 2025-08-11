# testapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('q1/', views.question_1, name='question_1'),
    path('q2/', views.question_2, name='question_2'),
    path('q3/', views.question_3, name='question_3'),
    path('q4/', views.question_4, name='question_4'),
    path('q5/', views.question_5, name='question_5'),
    path('q6/', views.question_6, name='question_6'),
    path('result/', views.result, name='result'), 
    path('reset/', views.reset, name='reset'),
]
