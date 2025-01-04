import os
import sqlite3
from tkinter import BOTH, END, LEFT, RIGHT, Y, Listbox, Scrollbar, Tk, Toplevel
import django
from django import forms
from django.contrib import messages
import shelve
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from fashion_scraper.models import Categoria, ListaDeseos, Usuario, Vestido
from fashion_scraper.populateDB import populate
from fashion_scraper.recommendations import calculateSimilarItems, getRecommendations, topMatches, transformPrefs
from .forms import BuscarCategoriaForm, BuscarColorYTallaForm,BuscarPrecioForm, BuscarVestidoForm, ModificarColorForm, UsuarioBusquedaForm, VestidoBusquedaForm 

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_scraping_fashion.settings")
django.setup()

def home(request):
    return HttpResponse("Welcome to the Web Scraper!")

def loadDict():
    Prefs = {}   
    shelf = shelve.open("dataRS.dat")
    ratings = ListaDeseos.objects.all()
    for ra in ratings:
        user = int(ra.idUsuario.idUsuario)
        itemid = int(ra.idVestido.idVestido)
        rating = float(ra.en_lista)
        Prefs.setdefault(user, {})
        Prefs[user][itemid] = rating
    shelf['Prefs'] = Prefs
    shelf['ItemsPrefs'] = transformPrefs(Prefs)  # aqui la clave es la pelicula en vez de un usuario. se intercambian las claves de usuario y película
    shelf['SimItems'] = calculateSimilarItems(Prefs, n=10)
    shelf.close()

def populateDatabase(request):
    populate()
    total_vestidos = Vestido.objects.count()
    total_categorias = Categoria.objects.count()
    total_usuarios = Usuario.objects.count()
    total_deseos = ListaDeseos.objects.count()
    messages.success(
        request,
        f"Se han cargado correctamente {total_vestidos} vestidos, {total_categorias} categorías, {total_usuarios} usuarios y {total_deseos} listas de deseos."
    )
    return HttpResponseRedirect('/index.html')


def loadRS(request):
    loadDict()
    return HttpResponseRedirect('/index.html')

def index(request):
    return render(request, 'index.html', {'STATIC_URL': settings.STATIC_URL})

def listar_vestidos(request):
    vestidos = Vestido.objects.all()
    return render(request, "listar_vestidos.html", {"vestidos": vestidos})

def listar_vestidos_tkinter(request):
    try:
        def mostrar_vestidos():
            ventana = Toplevel()
            ventana.title("Lista de Vestidos")
            sc = Scrollbar(ventana)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(ventana, width=150, yscrollcommand=sc.set)
            
            vestidos = Vestido.objects.all()

            if not vestidos.exists():
                lb.insert(END, "No hay vestidos disponibles en la base de datos.")
            else:
                for vestido in vestidos:
                    lb.insert(END, f"Nombre: {vestido.nombre}")
                    lb.insert(END, f"Tallas: {vestido.tallas}")
                    lb.insert(END, f"Color: {vestido.color}")
                    lb.insert(END, f"Precio: {vestido.precio}€")
                    lb.insert(END, f"Categoría: {', '.join(cat.nombre for cat in vestido.categoria.all())}")
                    lb.insert(END, f"Tienda: {vestido.tienda}")
                    lb.insert(END, "-" * 50)

            lb.pack(side=LEFT, fill=BOTH)
            sc.config(command=lb.yview)

        root = Tk()
        root.withdraw() 
        mostrar_vestidos()
        root.mainloop()

        return HttpResponse("Se abrió la ventana de Tkinter.")
    except Exception as e:
        return HttpResponse(f"Error al abrir la ventana de Tkinter: {e}")
    
# ============================ FUNCIONES DE BÚSQUEDA ============================
def buscar_por_color_talla(request):
    formulario= BuscarColorYTallaForm()
    vestidos = None
    color = None
    talla= None

    if request.method == "POST":
        formulario = BuscarColorYTallaForm(request.POST)
        if formulario.is_valid():
            color = formulario.cleaned_data["color"].strip().lower()
            talla = formulario.cleaned_data["talla"]
            vestidos = Vestido.objects.filter(color__iregex=rf'(?i)\b{color}\b', tallas__icontains=talla)

    else:
        formulario = BuscarColorYTallaForm()

    return render(request, "buscar_por_color_talla.html", {
        "formulario": formulario, 
        "vestidos": vestidos, 
        "color": color
    })

def buscar_por_precio(request):
    formulario= BuscarPrecioForm()
    vestidos = None
    precio = None

    if request.method == "POST":
        formulario = BuscarPrecioForm(request.POST)
        if formulario.is_valid():
            precio = formulario.cleaned_data["precio"]
            vestidos = Vestido.objects.filter(precio__lte=precio).order_by("precio")

    return render(request, "buscar_por_precio.html", {
        "formulario": formulario, 
        "vestidos": vestidos, 
        "precio": precio
    })

def buscar_por_categoria(request):
    formulario = BuscarCategoriaForm()
    vestidos = None
    categoria_seleccionada = None

    if request.method == "POST":
        formulario = BuscarCategoriaForm(request.POST)
        if formulario.is_valid():
            categoria_seleccionada = formulario.cleaned_data["categoria"]
            vestidos = Vestido.objects.filter(categoria=categoria_seleccionada)

    return render(request, "buscar_por_categoria.html", {
        "formulario": formulario,
        "vestidos": vestidos,
        "categoria_seleccionada": categoria_seleccionada
    })

def modificar_eliminar_color(request):
    buscar_form = BuscarVestidoForm()
    modificar_form = ModificarColorForm()
    colores = []
    vestido = None
    mensaje = None

    if request.method == "POST":
        if "buscar" in request.POST:
            buscar_form = BuscarVestidoForm(request.POST)
            if buscar_form.is_valid():
                nombre_vestido = buscar_form.cleaned_data["nombre_vestido"]
                vestidos = Vestido.objects.filter(nombre__icontains=nombre_vestido)

                if vestidos.exists():
                    vestido = vestidos.first()
                    colores = vestido.color.split(", ")
                    if not colores:
                        mensaje = "No hay colores asociados a este vestido."
                else:
                    mensaje = f"No se encontró ningún vestido con el nombre '{nombre_vestido}'."

        elif "modificar" in request.POST:
            modificar_form = ModificarColorForm(request.POST)
            nombre_vestido = request.POST.get("nombre_vestido")
            color_seleccionado = request.POST.get("color_seleccionado")
            if modificar_form.is_valid():
                nuevo_color = modificar_form.cleaned_data["nuevo_color"]
                vestidos = Vestido.objects.filter(nombre__icontains=nombre_vestido)

                if vestidos.exists():
                    vestido = vestidos.first()
                    colores = vestido.color.split(", ")

                    if color_seleccionado in colores:
                        colores[colores.index(color_seleccionado)] = nuevo_color
                        vestido.color = ", ".join(colores)
                        vestido.save()
                        mensaje = f"El color '{color_seleccionado}' fue modificado a '{nuevo_color}'."
                    else:
                        mensaje = f"El color '{color_seleccionado}' no se encontró en el vestido."

        elif "eliminar" in request.POST:
            nombre_vestido = request.POST.get("nombre_vestido")
            color_seleccionado = request.POST.get("color_seleccionado")
            vestidos = Vestido.objects.filter(nombre__icontains=nombre_vestido)

            if vestidos.exists():
                vestido = vestidos.first()
                colores = vestido.color.split(", ")

                if color_seleccionado in colores:
                    colores.remove(color_seleccionado)
                    vestido.color = ", ".join(colores)
                    vestido.save()
                    mensaje = f"El color '{color_seleccionado}' fue eliminado del vestido."
                else:
                    mensaje = f"El color '{color_seleccionado}' no se encontró en el vestido."

    return render(request, "modificar_eliminar_color.html", {
        "buscar_form": buscar_form,
        "modificar_form": modificar_form,
        "colores": colores,
        "vestido": vestido,
        "mensaje": mensaje,
    })

def recomendar_vestidos_usuario(request):
    formulario = UsuarioBusquedaForm()
    items = None
    usuario = None

    if request.method == "POST":
        formulario = UsuarioBusquedaForm(request.POST)

        if formulario.is_valid():
            idUsuario = formulario.cleaned_data["idUsuario"]
            usuario = get_object_or_404(Usuario, pk=idUsuario)

            with shelve.open("dataRS.dat") as shelf:
                Prefs = shelf.get("Prefs", None)

            if Prefs is not None:
                recomendaciones = getRecommendations(Prefs, idUsuario)[:2]
                items = [(Vestido.objects.get(pk=r[1]), r[0]) for r in recomendaciones]

    return render(request, "recomendar_vestidos_usuario.html", {
        "formulario": formulario,
        "items": items,
        "usuario": usuario,
    })


def mostrar_vestidos_similares(request):
    formulario = VestidoBusquedaForm()
    items = None
    vestido = None

    if request.method == "POST":
        formulario = VestidoBusquedaForm(request.POST)

        if formulario.is_valid():
            idVestido = formulario.cleaned_data["idVestido"]
            vestido = get_object_or_404(Vestido, pk=idVestido)

            with shelve.open("dataRS.dat") as shelf:
                ItemsPrefs = shelf.get("ItemsPrefs", None)

            if ItemsPrefs is not None:
                similares = topMatches(ItemsPrefs, idVestido, n=3)
                items = [(Vestido.objects.get(pk=s[1]), s[0]) for s in similares]

    return render(request, "mostrar_vestidos_similares.html", {
        "formulario": formulario,
        "items": items,
        "vestido": vestido,
    })

def mostrar_lista_deseos_usuario(request):
    formulario = UsuarioBusquedaForm()
    items = None
    usuario = None

    if request.method == "POST":
        formulario = UsuarioBusquedaForm(request.POST)

        if formulario.is_valid():
            idUsuario = formulario.cleaned_data["idUsuario"]
            usuario = get_object_or_404(Usuario, pk=idUsuario)
            # Filtrar solo los vestidos que están en la lista de deseos (en_lista = 1)
            items = ListaDeseos.objects.filter(idUsuario=usuario, en_lista=1)

    return render(request, "mostrar_lista_deseos_usuario.html", {
        "formulario": formulario,
        "items": items,
        "usuario": usuario,
    })

def buscar(request):
    return render(request, 'buscar.html')

def recomendar(request):
    return render(request, 'recomendar.html')
