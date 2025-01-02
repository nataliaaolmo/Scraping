from django.contrib import messages
import shelve
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from fashion_scraper.models import Categoria, ListaDeseos, Usuario, Vestido
from fashion_scraper.populateDB import populate
from fashion_scraper.recommendations import calculateSimilarItems, transformPrefs

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