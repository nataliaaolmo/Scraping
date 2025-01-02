import csv
import requests
from bs4 import BeautifulSoup

url = "https://www.parfois.com/es/es/ropa/vestidos/vestido-midi-con-lentejuelas/230087.html?dwvar_230087_color=_EC"

def run():
    scrape_references_parfois("referencias2.csv")

def scrape_references_parfois(output_file="referencias2.csv"):
    referencias = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    response = requests.get(url, headers=headers)

    # Depuración: guarda el HTML
    with open("parfois_product.html", "w", encoding="utf-8") as file:
        file.write(response.text)

    soup = BeautifulSoup(response.text, 'lxml')

    # Localizar el contenedor que contiene la referencia
    info = soup.find("div", class_="d-none d-md-block")  # Contenedor padre
    if info:
        info1 = info.find("span", class_="product-id")
        if info1:
            idVestido = info1.text.strip()
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
