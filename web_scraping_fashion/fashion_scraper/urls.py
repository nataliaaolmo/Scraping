from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('index.html/', views.index),
    path('populate/', views.populateDatabase),
    path('loadRS/', views.loadRS),
    path('listar_vestidos_tkinter/', views.listarVestidosTkinter, name='listarVestidosTkinter'),
    path("buscar/color/", views.buscarPorColorTalla, name="buscarPorColorTalla"),
    path("buscar/precio/", views.buscarPorPrecio, name="buscarPorPrecio"),
    path("buscar/categoria/", views.buscarPorCategoria, name="buscarPorCategoria"),
    path("modificar/", views.modificarEliminarColor, name="modificarEliminarColor"),
    path("recomendar/vestidos_usuario/", views.recomendarVestidosUsuario, name="recomendarVestidosUsuario"),
    path("recomendar/vestidos_similares/", views.mostrarVestidosSimilares, name="mostrarVestidosSimilares"),
    path("recomendar/lista_deseos/", views.mostrarListaDeseosUsuario, name="mostrarListaDeseosUsuario"),
    path('buscar/', views.buscar, name='buscar'),
    path('recomendar/', views.recomendar, name='recomendar'),
]
