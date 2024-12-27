# Scraping
A scraping of some inditex webs such as  **Stradivarius**, **Pull & Bear**, and **Bershka**. The goal is to extract product-related data such as names, prices, categories or sizes.

## Objective
Organize the scraped data into a structured format for further analysis.

## Features
The tools that will be used in this project are Beautifulsoup, Whoosh, Sistema de Recomendación y Django

## Requirements
To run this project, you will need:

- **Programming Language**: Python 3.8+
- **Libraries**:
  - `whoosh`
  - `beautifulsoup4`
  - `django`


## Setup
1. Clone this repository:
```bash
git clone https://github.com/nataliaaolmo/web-scraping-fashion.git
```
2. Navigate to the project directory:
```bash
cd web-scraping-fashion
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. (Optional) Set up environment variables for API keys or sensitive data in a `.env` file.

## Usage


## File Structure
```
web-scraping-fashion/
├── data/                  # Directory for storing scraped data
├── scripts/               # Python scripts for scraping
│   ├── scrape_stradivarius.py
│   ├── scrape_pullandbear.py
│   └── scrape_bershka.py
├── requirements.txt       # List of Python dependencies
├── README.md              # Project documentation
└── .env                   # Environment variables (not included in repo)
```

## Notes
- This project is for educational purposes only
