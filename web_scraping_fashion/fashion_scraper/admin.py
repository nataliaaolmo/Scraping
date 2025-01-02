from django.contrib import admin
from .models import Usuario, Categoria, ListaDeseos, Vestido

# Registra los modelos para que sean visibles en el admin
admin.site.register(Usuario)
admin.site.register(Categoria)
admin.site.register(ListaDeseos)
admin.site.register(Vestido)
