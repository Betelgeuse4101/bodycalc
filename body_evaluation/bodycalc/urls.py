from django.urls import path
from . import views

app_name = 'bodycalc'

urlpatterns = [
    path('', views.evaluation_form, name='evaluation_form'),
    path('results/<int:pk>/', views.results, name='results'),
]