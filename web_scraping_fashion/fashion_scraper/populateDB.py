import csv
import random
import re
from tkinter import messagebox
from bs4 import BeautifulSoup
import ssl
import os
import urllib.request
import sys
import django
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, NUMERIC, KEYWORD

#directorio base del proyecto a sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuración entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_scraping_fashion.settings')
django.setup()
from fashion_scraper.models import Usuario, Categoria, ListaDeseos, Vestido

path = "data"
urls = [
        "https://www.lamoneria.es/categoria/vestidos/page/",
        "https://www.sachascloset.com/categoria-producto/ropa/vestidos/page/",
    ]

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def resetTableSequences():
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='fashion_scraper_vestido';")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='fashion_scraper_categoria';")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='fashion_scraper_lista_deseos';")

def populate():
    Categoria.objects.all().delete()
    Vestido.objects.all().delete()
    ListaDeseos.objects.all().delete()

    resetTableSequences()  

    populateCategories()
    users = populateUsers()
    dresses = populateDresses(urls)
    generateNewListaDeseos(users, dresses)
    populateWishList(users, dresses)
    indexDresses()

# ===================== FUNCIONES AUXILIARES =====================

def fetch_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req)

# ===================== CATEGORÍAS ===================== 

def populateCategories():
    Categoria.objects.all().delete()

    categorias_set = set()  

    for url in urls:
        if "lamoneria" in url:
            for num_paginas in range(1,3):
                url_pagina=url+str(num_paginas)
                f = urllib.request.urlopen(url_pagina)
                s = BeautifulSoup(f,"lxml")
                categorias_pagina = s.find_all("div", class_="wd-product-cats")
                for contenedor in categorias_pagina:
                    categorias = contenedor.find_all("a", rel="tag") 
                    for categoria in categorias:
                        categorias_texto = categoria.text.strip()
                        for subcategoria in categorias_texto.split(","):
                            categorias_set.add(subcategoria.strip())
        if "sachas" in url:
            for num_paginas in range(1,3):
                url_pagina=url+str(num_paginas)
                f = urllib.request.urlopen(url_pagina)
                s = BeautifulSoup(f,"lxml")
                vestidos = s.find("ul", class_="products columns-3").find_all("li")
                for vestido in vestidos:
                    f = fetch_html(vestido.find("a")["href"])
                    soup = BeautifulSoup(f, "lxml")
                    categorias_vestido = extractCategories(soup)      
                    for subcategoria in categorias_vestido: 
                        categorias_set.add(subcategoria)

    for nombre in categorias_set:
        Categoria.objects.get_or_create(nombre=nombre)

# ===================== USUARIOS =====================
def populateUsers():
    Usuario.objects.all().delete()
    lista = []
    dict = {}

    with open(path + "/usuarios.csv", "r") as fileobj:
        for line in fileobj.readlines():
            rip = str(line.strip()).split(',')
            u = Usuario(idUsuario=rip[0], edad=rip[1], talla=rip[2])
            lista.append(u)
            dict[rip[0]] = u
    
    Usuario.objects.bulk_create(lista)
    return dict

# ===================== VESTIDOS =====================
def populateDresses(urls):
    lista_vestidos = []
    vestidos_dict = {}

    for url in urls:
        for num_paginas in range(1, 3):
            url_pagina = url + str(num_paginas)
            f = fetch_html(url_pagina)
            soup = BeautifulSoup(f, "lxml")

            if "lamoneria" in url:
                vestidos = soup.find_all("div", class_="product-wrapper")
            elif "sachas" in url:
                vestidos = soup.find("ul", class_="products columns-3").find_all("li")
            else:
                vestidos = []

            for vestido_html in vestidos:
                processDress(vestido_html, lista_vestidos, vestidos_dict, tienda="La Moneria" if "lamoneria" in url else "Sachas Closet")

    unique_vestidos = []
    seen_vestidos = set()

    for vestido in lista_vestidos:
        key = (vestido.nombre, vestido.tienda)
        if key not in seen_vestidos and not Vestido.objects.filter(nombre=vestido.nombre, tienda=vestido.tienda).exists():
            unique_vestidos.append(vestido)
            seen_vestidos.add(key)

    for vestido in unique_vestidos:
        vestido.idVestido = None

    Vestido.objects.bulk_create(unique_vestidos)

    return vestidos_dict


# ===================== PROCESAMIENTO DE UN VESTIDO =====================

def processDress(producto, vestidos, vestidos_dict, tienda):
    try:
        f = fetch_html(producto.find("a")["href"])
        soup = BeautifulSoup(f, "lxml")
        if tienda == "La Moneria":
            info = soup.find("div", class_="summary-inner")
        elif tienda == "Sachas Closet":
            info = soup.find("div", class_="summary entry-summary")

        titulo = info.find("h1").text.strip()
        precio_raw = info.find("p", class_="price").select_one(".woocommerce-Price-amount bdi").get_text(strip=True)
        precio = float(precio_raw.replace('€', '').replace(',', '.'))

        if Vestido.objects.filter(nombre=titulo, tienda=tienda).exists():
            print(f"Vestido ya existe: {titulo}")
            return

        colores = extractColors(titulo, soup)
        categorias_vestido = extractCategories(soup)
        categorias_objs = [
            Categoria.objects.get_or_create(nombre=categoria_nombre)[0]
            for categoria_nombre in categorias_vestido
        ]

        tallas = extractSizesMoneria(soup) if tienda == "La Moneria" else extractSizesSachas(soup)

        vestido = Vestido(
            nombre=titulo,
            tallas=tallas,
            color=colores,
            precio=precio,
            tienda=tienda,
        )
        vestido.save() 
        vestido.categoria.set(categorias_objs)  
        vestido.save()

        vestidos.append(vestido)
        vestidos_dict[vestido.idVestido] = vestido

        print(f"Procesado vestido: {titulo}, Precio: {precio}, Categorías: {categorias_vestido}, Tallas: {tallas}")

    except Exception as e:
        print(f"Error procesando vestido: {e}")



# ===================== EXTRACCIÓN DE DATOS =====================

def extractColors(titulo, soup):
    colores = soup.find_all("span", class_="wd-swatch-text")
    if colores:
        return ", ".join([color.text.strip() for color in colores])
    return titulo.split()[1] if len(titulo.split()) > 1 else "Color único"

def extractCategories(soup):
    categorias = soup.find("span", class_="posted_in")
    if categorias:
        categorias_texto = categorias.find_all("a", rel="tag")
        return list(set(c.text.strip() for c in categorias_texto))
    return []


def extractSizesMoneria(soup):
    descripcion = soup.find("div", class_="wc-tab-inner")
    tallas = []

    if descripcion:
        descripcion_completa = " ".join([p.get_text() for p in descripcion.find_all("p")])

        match = re.search(r'tallaje[s]?\s+para\s+([\d\s,.-]+)', descripcion_completa, re.IGNORECASE)
        if match:
            tallas_encontradas = re.findall(r'\d+', match.group(1))
            tallas.extend(tallas_encontradas)
    tallas = sorted(set(tallas), key=int)
    tallas_str = ", ".join(tallas)
    return tallas_str

def extractSizesSachas(soup):
    mapa_tallas = {
        "S": 34,
        "M": 36,
        "L": 38,
        "XL": 40
    }

    tallas = []
    descripcion = soup.find("div", class_="woocommerce-product-details__short-description")
    descripcion_completa = " ".join([p.get_text() for p in descripcion.find_all("p")])

    # Buscar números directamente
    numeros = re.findall(r'\d+', descripcion_completa)
    tallas.extend(numeros)

    # Buscar letras (S, M, L, XL) y mapear a números
    letras = re.findall(r'\b(S|M|L|XL)\b', descripcion_completa, re.IGNORECASE)
    tallas.extend([mapa_tallas[letra.upper()] for letra in letras])

    # Eliminar duplicados y ordenar
    tallas_unicas = sorted(set(map(int, tallas)))

    return tallas_unicas

# ===================== INDEXADO CON WHOOSH =====================
def indexDresses():
    schema = Schema(
        nombre=TEXT(stored=True),
        tallas=TEXT(stored=True), #alomejot rb hay que poner el commas=True
        color=KEYWORD(stored=True, commas=True),
        precio=NUMERIC(stored=True, decimal_places=2),
        categoria=KEYWORD(stored=True, commas=True),
        tienda=TEXT(stored=True),
    )

    import os
    if not os.path.exists("Index"):
        os.mkdir("Index")
    ix = create_in("Index", schema)

    writer = ix.writer()
    for vestido in Vestido.objects.all():
        categorias = ', '.join([cat.nombre for cat in vestido.categoria.all()]) 
        writer.add_document(
            nombre=vestido.nombre,
            tallas=vestido.tallas,
            color=vestido.color,
            precio=float(vestido.precio),
            categoria=categorias,
            tienda=vestido.tienda,
        )
    writer.commit()
    messagebox.showinfo("Fin de indexado",
                        "Se han indexado " + str(len(Vestido.objects.all())) + " vestidos")

# ===================== LISTA DE DESEOS =====================
def generateNewListaDeseos(users, dresses):
    """
    Genera un archivo lista_deseos.csv basado en los usuarios y vestidos cargados.
    """
    try:
        output_file = os.path.join(path, "lista_deseos.csv") 
        lista_deseos_data = []

        for user_id, user_obj in users.items():
            for dress_id, dress_obj in dresses.items():
                if user_id and dress_id:  
                    en_lista = random.randint(0, 1) 
                    lista_deseos_data.append([user_id, dress_id, en_lista])  

        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(lista_deseos_data) 

        print(f"Archivo lista_deseos.csv generado con {len(lista_deseos_data)} entradas.")
    except Exception as e:
        print(f"Error en generate_new_lista_deseos: {e}")


def populateWishList(u, d):
    ListaDeseos.objects.all().delete()
    lista = []

    print("Procesando lista_deseos.csv...")

    with open(path + "/lista_deseos.csv", "r") as fileobj:
        for line in fileobj.readlines():
            try:
                rip = str(line.strip()).split(',')

                if len(rip) < 3 or not rip[0].isdigit() or not rip[1].isdigit():
                    print(f"Línea mal formateada: {line.strip()}")
                    continue  

                idUsuario = rip[0]
                idVestido = int(rip[1])
                en_lista = int(rip[2])

                if idUsuario in u and idVestido in d:  
                    lista.append(ListaDeseos(idUsuario=u[idUsuario], idVestido=d[idVestido], en_lista=en_lista))
                else:
                    print(f"Usuario o vestido no encontrado: Usuario={idUsuario}, Vestido={idVestido}")
            except Exception as e:
                print(f"Error procesando línea {line.strip()}: {e}")

    ListaDeseos.objects.bulk_create(lista)
    print(f"Total de listas de deseos creadas: {len(lista)}")




