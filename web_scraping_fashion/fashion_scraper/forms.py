# encoding:utf-8
from django import forms

from fashion_scraper.models import Categoria

class UsuarioBusquedaForm(forms.Form):
    idUsuario = forms.IntegerField(
        label="ID del Usuario",
        widget=forms.NumberInput(attrs={'placeholder': 'Introduce el ID del usuario'})
    )

class BuscarColorYTallaForm(forms.Form):
    color = forms.CharField(
        max_length=50,
        label="Color",
        widget=forms.TextInput(attrs={"placeholder": "Introduce un color"})
    )
    talla = forms.CharField(
        max_length=10,
        label="Talla",
        widget=forms.TextInput(attrs={"placeholder": "Introduce una talla"})
    )

class BuscarPrecioForm(forms.Form):
    precio = forms.FloatField(
        label="Precio máximo", 
        widget=forms.NumberInput(attrs={'placeholder': 'Introduce un precio'})
    )

class BuscarCategoriaForm(forms.Form):
    categoria = forms.ModelChoiceField(
        label="Selecciona una categoría",
        queryset=Categoria.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class BuscarVestidoForm(forms.Form):
    nombre_vestido = forms.CharField(
        label="Nombre del Vestido",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Introduce el nombre del vestido'})
    )

class ModificarColorForm(forms.Form):
    nuevo_color = forms.CharField(
        label="Nuevo Color",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Introduce el nuevo color'})
    )

class VestidoBusquedaForm(forms.Form):
    idVestido = forms.IntegerField(
        label="ID del Vestido",
        widget=forms.NumberInput(attrs={'placeholder': 'Introduce el ID del vestido'})
    )
