# Scraping
A scraping of some web fashion webs. The goal is to extract product-related data such as names, prices, categories or sizes.

## Objective
Organize the scraped data into a structured format for further analysis.

## Features
The tools that will be used in this project are Beautifulsoup, Whoosh, Sistema de Recomendación y Django

## Requirements
To run this project, you will need:

- **Programming Language**: Python 3.8+
- **Libraries**:
  - `asgiref==3.8.1`
  - `beautifulsoup4==4.12.3`
  - `certifi==2024.12.14`
  - `charset-normalizer==3.4.1`
  - `Django==5.1.4`
  - `django-extensions==3.2.3`
  - `idna==3.10`
  - `lxml==5.3.0`
  - `requests==2.32.3`
  - `soupsieve==2.6`
  - `sqlparse==0.5.3`
  - `tzdata==2024.2`
  - `urllib3==2.3.0`
  - `Whoosh==2.7.4`

## Setup
1. Clone this repository:
```bash
git clone https://github.com/nataliaaolmo/web-scraping-fashion.git
```
2. Navigate to the project directory:
```bash
cd web_scraping_fashion
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. (Optional) Set up environment variables for API keys or sensitive data in a `.env` file.
```bash
python -m venv nombre_del_entorno
nombre_del_entorno\Scripts\activate
```

6. Start the applicaction
```bash
python manage.py runserver
```

## File Structure
```
web-scraping-fashion/
├── data/                  # Directory for storing scraped data
│   ├── lista_deseos.csv
│   └── usuarios.csv
├── fashion_scraper/               # Python scripts for scraping
│   ├── scripts/
│   ├── static/
│   │   └── styles.css
│   ├── templates/
│   │   ├── buscar_por_categoria.html
│   │   ├── buscar_por_color_talla.html
│   │   ├── buscar_por_precio.html
│   │   ├── buscar.html
│   │   ├── index.html
│   │   ├── master.html
│   │   ├── modificar_eliminar_color.html
│   │   ├── mostrar_lista_deseos_usuario.html
│   │   ├── mostrar_vestidos_similares.html
│   │   ├── recomendar_vestidos_usuario.html
│   │   └── recomendar.html
│   ├── forms.py
│   ├── models.py
│   ├── populateDB.py
│   ├── recommendations.py
│   ├── urls.py
│   ├── views.py
│   └── web_scraping_fashion/
│   │   └── settings.py
├── db.sqlite3
├── manage.py
├── requirements.txt       # List of Python dependencies
├── README.md              # Project documentation
└── .env                   # Environment variables (not included in repo)
```

## Notes
- This project is for educational purposes only
