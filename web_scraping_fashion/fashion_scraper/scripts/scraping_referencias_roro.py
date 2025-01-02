import csv
import requests
from bs4 import BeautifulSoup

url = "https://rociomoscosio.com/producto/vestido-lea/"

def run():
    scrape_references_parfois("referencias3.csv")

def scrape_references_parfois(output_file="referencias3.csv"):
    referencias = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    response = requests.get(url, headers=headers)

    # Depuración: guarda el HTML
    with open("roro_product.html", "w", encoding="utf-8") as file:
        file.write(response.text)

    soup = BeautifulSoup(response.text, 'lxml')

    # Buscar el contenedor correcto
    info = soup.find("span", class_="sku_wrapper")
    if info:
        ref_span = info.find("span", class_="sku")  # Asegurarse de buscar el span correcto
        if ref_span:
            idVestido = ref_span.text.strip()  # Extraer texto y aplicar strip
            referencias.add(idVestido)
        else:
            print("No se encontró la referencia dentro del contenedor.")
    else:
        print("No se encontró el contenedor principal.")

    # Guardar referencias en un archivo CSV
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["idVestido"])  # Cabecera
        for ref in referencias:
            writer.writerow([ref])

if __name__ == "__main__":
    run()
