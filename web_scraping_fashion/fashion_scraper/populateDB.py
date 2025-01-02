import csv
import random
import re
from bs4 import BeautifulSoup
import ssl
import os
import urllib.request
import sys
import django

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
        # "https://rociomoscosio.com/categoria-producto/vestidos/"
    ]

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def reset_table_sequences():
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='fashion_scraper_vestido';")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='fashion_scraper_lista_deseos';")

def populate():
    Categoria.objects.all().delete()
    Vestido.objects.all().delete()
    ListaDeseos.objects.all().delete()

    reset_table_sequences()  

    populateCategories()
    users = populateUsers()
    dresses = populateDresses(urls)
    generate_new_lista_deseos(users, dresses)
    populateWishList(users, dresses)

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
                    categorias_vestido = extract_categories(soup)      
                    for subcategoria in categorias_vestido: 
                        categorias_set.add(subcategoria)

    Categoria.objects.bulk_create([Categoria(nombre=nombre) for nombre in categorias_set])

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
                process_dress(vestido_html, lista_vestidos, vestidos_dict, tienda="La Moneria" if "lamoneria" in url else "Sachas Closet")

    # Guardar todos los vestidos en la base de datos
    unique_vestidos = []
    seen_vestidos = set()

    for vestido in lista_vestidos:
        key = (vestido.nombre, vestido.tienda)
        if key not in seen_vestidos:
            unique_vestidos.append(vestido)
            seen_vestidos.add(key)

    Vestido.objects.bulk_create(unique_vestidos)

    for vestido in unique_vestidos:
        vestido_db = Vestido.objects.get(nombre=vestido.nombre, tienda=vestido.tienda)
        vestidos_dict[vestido_db.idVestido] = vestido_db 

    return vestidos_dict


# ===================== PROCESAMIENTO DE UN VESTIDO =====================

def process_dress(producto, vestidos, vestidos_dict, tienda):
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

        exists = Vestido.objects.filter(nombre=titulo, tienda=tienda).exists()
        if exists:
            print(f"Vestido ya existe: {titulo}")
            return

        if tienda == "La Moneria":
            colores = extract_colors(titulo, soup)
        elif tienda == "Sachas Closet":
            colores = titulo.split()[1]

        categorias_vestido = extract_categories(soup)
        categorias_objs = []
        for categoria_nombre in categorias_vestido:
            categoria_obj, _ = Categoria.objects.get_or_create(nombre=categoria_nombre)
            categorias_objs.append(categoria_obj)

        if tienda == "La Moneria":
            tallas = extract_sizes_moneria(soup)
        elif tienda == "Sachas Closet":
            tallas = extract_sizes_sachas(soup)

        vestido = Vestido(
            nombre=titulo,
            tallas=tallas,
            color=colores,
            precio=precio,
            tienda=tienda,
        )
        vestidos.append(vestido)  # No asignamos idVestido manualmente
        vestidos_dict[vestido.idVestido] = vestido  # Usamos el nombre como clave

        print(f"Procesado vestido: {titulo}, Precio: {precio}, Categorías: {categorias_vestido}, Tallas: {tallas}")

    except Exception as e:
        print(f"Error procesando vestido: {e}")


# ===================== EXTRACCIÓN DE DATOS =====================

def extract_colors(titulo, soup):
    colores = soup.find_all("span", class_="wd-swatch-text")
    if colores:
        return ", ".join([color.text.strip() for color in colores])
    return titulo.split()[1] if len(titulo.split()) > 1 else "Color único"

def extract_categories(soup):
    categorias = soup.find("span", class_="posted_in")
    if categorias:
        categorias_texto = categorias.find_all("a", rel="tag")
        return [c.text.strip() for c in categorias_texto]  # Devolver una lista
    return ["Sin categoría"]


def extract_sizes_moneria(soup):
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

def extract_sizes_sachas(soup):
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
# def index_dresses(lista_vestidos):
#     schema = Schema(
#         idVestido=TEXT(stored=True),
#         nombre=TEXT(stored=True),
#         categoria=TEXT(stored=True),
#         color=TEXT(stored=True),
#         precio=NUMERIC(stored=True)
#     )

#     import os
#     if not os.path.exists("whoosh_index"):
#         os.mkdir("whoosh_index")
#     ix = create_in("whoosh_index", schema)

#     writer = ix.writer()
#     for vestido in lista_vestidos:
#         categorias = ', '.join([cat.nombre for cat in vestido.categoria.all()]) 
#         writer.add_document(
#             idVestido=vestido.idVestido,
#             nombre=vestido.nombre,
#             categoria=categorias,
#             color=vestido.color,
#             precio=float(vestido.precio)
#         )
#     writer.commit()

# ===================== LISTA DE DESEOS =====================
def generate_new_lista_deseos(users, dresses):
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




