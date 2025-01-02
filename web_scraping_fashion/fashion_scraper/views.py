import os
import sqlite3
from tkinter import BOTH, END, LEFT, RIGHT, Y, Listbox, Menu, Scrollbar, Tk, Toplevel
import django
from django.contrib import messages
import shelve
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import subprocess

from fashion_scraper.models import Categoria, ListaDeseos, Usuario, Vestido
from fashion_scraper.populateDB import populate
from fashion_scraper.recommendations import calculateSimilarItems, transformPrefs

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

# def listar_vestidos2(cursor):
#     v = Toplevel()
#     sc = Scrollbar(v)
#     sc.pack(side=RIGHT, fill=Y)
#     lb = Listbox(v, width=150, yscrollcommand=sc.set)
#     for row in cursor:
#         s = 'VESTIDO: ' + row[0]
#         lb.insert(END, s)
#         lb.insert(END, "-----------------------------------------------------")
#         s = "     NOMBRE: " + str(row[1]) + ' | TALLAS: ' + row[2] + ' | COLOR: ' + row[3] + ' | PRECIO: ' + row[4] + ' | CATEGORIA: ' + row[5] + ' | TIENDA: ' + row[6]
#         lb.insert(END, s)
#         lb.insert(END, "\n\n")
#     lb.pack(side=LEFT, fill=BOTH)
#     sc.config(command=lb.yview)  

# def ventana_principal():
#     def listar():
#         conn = sqlite3.connect('db.sqlite3')
#         conn.text_factory = str
#         cursor = conn.execute("SELECT NOMBRE, TALLAS, COLOR, PRECIO, CATEGORIA, TIENDA FROM VESTIDO")
#         conn.close
#         listar_vestidos2(cursor)

#     raiz = Tk()

#     menu = Menu(raiz)

#     #DATOS
#     menudatos = Menu(menu, tearoff=0)
#     menudatos.add_command(label="Listar", command=listar)
#     menudatos.add_command(label="Salir", command=raiz.quit)
#     menu.add_cascade(label="Datos", menu=menudatos)

#     #BUSCAR
#     menubuscar = Menu(menu, tearoff=0)
#     # menubuscar.add_command(label="Denominación", command=buscar_por_denominacion)
#     # menubuscar.add_command(label="Precio", command=buscar_por_precio)
#     # menubuscar.add_command(label="Uvas", command=buscar_por_uvas)
#     menu.add_cascade(label="Buscar", menu=menubuscar)

#     raiz.config(menu=menu)

#     raiz.mainloop()

def listar_vestidos_tkinter(request):
    try:
        # Crea la ventana de Tkinter
        def mostrar_vestidos():
            ventana = Toplevel()
            ventana.title("Lista de Vestidos")
            sc = Scrollbar(ventana)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(ventana, width=150, yscrollcommand=sc.set)
            
            # Obtén los datos reales de la base de datos
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
        root.withdraw()  # Oculta la ventana raíz
        mostrar_vestidos()
        root.mainloop()

        return HttpResponse("Se abrió la ventana de Tkinter.")
    except Exception as e:
        return HttpResponse(f"Error al abrir la ventana de Tkinter: {e}")