# encoding:utf-8
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Categoria(models.Model):
    idCategoria = models.AutoField(primary_key=True)
    nombre = models.TextField(verbose_name='Categoría', unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ('idCategoria', )


class Usuario(models.Model):
    idUsuario = models.IntegerField(primary_key=True)
    edad=models.IntegerField(verbose_name='Edad')
    talla=models.TextField(verbose_name='Talla')

    def __str__(self):
        return str(self.idUsuario)

    class Meta:
        ordering = ('idUsuario', )


class Vestido(models.Model):
    idVestido = models.AutoField(primary_key=True)
    nombre = models.TextField(verbose_name='Nombre', unique=True)
    tallas=models.TextField(verbose_name='Tallas')
    color=models.TextField(verbose_name='Color')
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    categoria = models.ManyToManyField(Categoria, related_name="vestidos")
    tienda=models.TextField(verbose_name='Tienda')
    listas_deseos = models.ManyToManyField(Usuario, through='ListaDeseos')

    def __str__(self):
        return f"{self.nombre} (ID: {self.idVestido})"

    class Meta:
        ordering = ('idVestido', )


class ListaDeseos(models.Model):
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    idVestido = models.ForeignKey(Vestido, on_delete=models.CASCADE)
    en_lista = models.IntegerField(verbose_name='En lista')

    def __str__(self):
        return f"{self.idUsuario} - {self.idVestido}: {self.en_lista}"

    class Meta:
        ordering = ('idUsuario', 'idVestido', )
