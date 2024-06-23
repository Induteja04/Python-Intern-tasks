import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define the base URL and the list to store the data
base_url = "http://books.toscrape.com/"
books = []

# Function to scrape a single page
def scrape_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    book_containers = soup.find_all('article', class_='product_pod')

    page_books = []
    for book in book_containers:
        title = book.h3.a['title']
        price = book.find('p', class_='price_color').text
        page_books.append([title, price])

    return page_books

# Scrape the first few pages (for example, first 5 pages)
for page in range(1, 6):
    url = base_url.format(page)
    books_on_page = scrape_page(url)
    books.extend(books_on_page)

# Create a DataFrame and save to CSV
df = pd.DataFrame(books, columns=['Title', 'Price'])
df.to_csv('books.csv', index=False)
print("Data saved to books.csv")
