import csv
import requests
from bs4 import BeautifulSoup

base_url = "https://www2.hm.com/es_es/mujer/compra-por-producto/vestidos.html"
pages = [base_url, f"{base_url}?page=2"]

def run():
    scrape_references_hym("referencias.csv")

def scrape_references_hym(output_file="referencias.csv"):
    referencias = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www2.hm.com/es_es/index.html',
        'Connection': 'keep-alive',
    }

    for page_index, page_url in enumerate(pages, start=1):
        try:
            print(f"Scraping página: {page_url}")
            response = requests.get(page_url, headers=headers)
            
            # Guardar el HTML de la página independientemente del estado
            html_filename = f"hm_page_{page_index}.html"
            with open(html_filename, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"Página guardada en: {html_filename}")

            # Verificar el estado HTTP
            response.raise_for_status()  # Genera una excepción para códigos de error HTTP

            # Parsear el contenido de la página
            soup = BeautifulSoup(response.text, 'lxml')
            productos = soup.find_all("article", class_="hm-product-item")
            if not productos:
                print(f"No se encontraron productos en la página: {page_url}")
                continue

            for producto in productos:
                producto_url = producto.find("a", class_="link")["href"]
                full_url = f"https://www2.hm.com{producto_url}"
                print(f"Accediendo al producto: {full_url}")

                # Solicita la página de detalles del producto
                producto_response = requests.get(full_url, headers=headers)
                producto_response.raise_for_status()
                producto_soup = BeautifulSoup(producto_response.text, 'lxml')

                idVestido_span = producto_soup.find("span", class_="product-article-code")
                if idVestido_span:
                    idVestido = idVestido_span.text.strip()
                    referencias.add(idVestido)
                    print(f"Referencia añadida: {idVestido}")
                else:
                    print(f"No se encontró el código del producto en {full_url}")

        except requests.exceptions.RequestException as e:
            print(f"Error accediendo a la página: {page_url}. Detalle: {e}")

    # Guardar referencias en un archivo CSV
    if referencias:
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["idVestido"])  # Cabecera
            for ref in referencias:
                writer.writerow([ref])
        print(f"Referencias guardadas en {output_file}")
    else:
        print("No se encontraron referencias para guardar.")

if __name__ == "__main__":
    run()
