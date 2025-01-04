from django.urls import path

from . import views

urlpatterns = [
    #path('', views.home, name='home'), 
    path('', views.index),
    path('index.html/', views.index),
    path('populate/', views.populateDatabase),
    path('loadRS/', views.loadRS),
    path('listar_vestidos_tkinter/', views.listar_vestidos_tkinter, name='listar_vestidos_tkinter'),
    path("buscar/color/", views.buscar_por_color_talla, name="buscar_por_color_talla"),
    path("buscar/precio/", views.buscar_por_precio, name="buscar_por_precio"),
    path("buscar/categoria/", views.buscar_por_categoria, name="buscar_por_categoria"),
    path("modificar/", views.modificar_eliminar_color, name="modificar_eliminar_color"),
    path("recomendar/vestidos_usuario/", views.recomendar_vestidos_usuario, name="recomendar_vestidos_usuario"),
    path("recomendar/vestidos_similares/", views.mostrar_vestidos_similares, name="mostrar_vestidos_similares"),
    path("recomendar/lista_deseos/", views.mostrar_lista_deseos_usuario, name="mostrar_lista_deseos_usuario"),
    path('buscar/', views.buscar, name='buscar'),
    path('recomendar/', views.recomendar, name='recomendar'),
]
