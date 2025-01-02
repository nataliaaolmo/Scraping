from django.urls import path

from . import views

urlpatterns = [
    #path('', views.home, name='home'), 
    path('', views.index),
    path('index.html/', views.index),
    path('populate/', views.populateDatabase),
    path('loadRS/', views.loadRS),
    path('listar_vestidos_tkinter/', views.listar_vestidos_tkinter, name='listar_vestidos_tkinter'),
]
