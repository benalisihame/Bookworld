import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup
import os



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SALES_PATH = os.path.join(BASE_DIR, "sales_raw.csv")

DB_PATH = os.path.join(BASE_DIR, "bookworld_reference.db")

BOOKS_URL = "https://books.toscrape.com/"

API_URL = "https://api.frankfurter.dev/v2/rate/gbp/eur"


def extract_sales():

    try:
        sales = pd.read_csv(SALES_PATH)

        print("Sales data extracted successfully.")
        print(f"Number of sales: {len(sales)}")

        return sales

    except Exception as error:
        print(f"Error extracting sales: {error}")
        raise



def extract_reference():


    try:

        # Connexion à la base SQLite
        conn = sqlite3.connect(DB_PATH)

        # Extraction de la table countries
        countries = pd.read_sql_query(
            "SELECT * FROM countries",
            conn
        )

        # Extraction de la table channels
        channels = pd.read_sql_query(
            "SELECT * FROM channels",
            conn
        )

        # Extraction de la table category_rules
        category_rules = pd.read_sql_query(
            "SELECT * FROM category_rules",
            conn
        )

        # Fermeture de la connexion
        conn.close()

        print("Reference data extracted successfully.")

        return {
            "countries": countries,
            "channels": channels,
            "category_rules": category_rules
        }

    except Exception as error:

        print(f"Error extracting reference data: {error}")

        raise


def extract_books():


    try:

        # Envoyer une requête au site
        response = requests.get(BOOKS_URL, timeout=15)

        # Vérifier que la requête a fonctionné
        response.raise_for_status()

        # Analyser le contenu HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Récupérer toutes les fiches de livres
        articles = soup.find_all(
            "article",
            class_="product_pod"
        )

        books_list = []

        # Parcourir chaque livre
        for article in articles:

            # Extraire le titre
            title = article.find("h3").a.get("title")

            # Extraire le prix
            price = article.find(
                "p",
                class_="price_color"
            ).text.strip()

            # Convertir en nombre pour une meilleure lisibilité
            price = price.replace("Â", "").replace("£", "")
            price = float(price)

            # Extraire la disponibilité
            availability = article.find(
                "p",
                class_="instock availability"
            ).text.strip()

            # Extraire la note
            rating_class = article.find(
                "p",
                class_="star-rating"
            ).get("class")

            rating = rating_class[1]

            # Ajouter les informations dans une liste
            books_list.append({
                "book_name": title,
                "price_gbp": price,
                "availability": availability,
                "rating": rating
            })

        # Transformer la liste en DataFrame
        books = pd.DataFrame(books_list)

        print("Books extracted successfully.")
        print(f"Number of books extracted: {len(books)}")

        return books

    except Exception as error:

        print(f"Error extracting books: {error}")
        raise



if __name__ == "__main__":

    books = extract_books()

    print("\nBOOKS SCRAPED")
    print(books.head())

    print("\nCOLUMNS")
    print(books.columns)

    print("\nNUMBER OF BOOKS")
    print(len(books))

