import requests
from bs4 import BeautifulSoup as bs
import datetime
import json
from concurrent.futures import ThreadPoolExecutor

def get_article_content(link):
    article_detail_response = requests.get(link)
    article_detail_content = article_detail_response.content
    article_detail_soup = bs(article_detail_content, 'html.parser')
    return article_detail_soup.find('div', attrs={'itemprop': 'articleBody'}).text

def process_article(article):
    article_header = article.find('div', attrs={'class': 'article-header'})
    link = article_header.find('a').get('href')
    link = "https://uchtepatumani.uz" + link
    title = article_header.find('a').text.strip()
    access_date = datetime.datetime.now()

    article_content = get_article_content(link)
    return {
        "title": title,
        "link": link,
        "access_date": access_date.strftime("%Y-%m-%d %H:%M:%S"),
        "text": article_content.strip()
    }

def fetch_articles(url):
    response = requests.get(url)
    content = response.content
    soup = bs(content, 'html.parser')

    articles = soup.find('div', attrs={'class': 'article-list'})
    all_articles = articles.find_all('div', attrs={'class': 'article'})

    article_data = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        article_data.extend(executor.map(process_article, all_articles))

    return article_data

# Starting URL
base_url = "https://uchtepatumani.uz/uz/matb-ot-hizmati/n-ili-lar"
response = requests.get(base_url)
content = response.content
soup = bs(content, 'html.parser')

pagination = soup.find('ul', class_='pagination')
max_page = int(pagination.find_all(class_='page-link')[-3].text.strip())

all_article_data = []

for start in range(0, max_page * 12, 12):
    url = f"{base_url}?start={start}"
    all_article_data.extend(fetch_articles(url))

# Save the data to a JSON file
with open("articles.json", "w", encoding="utf-8") as f:
    json.dump(all_article_data, f, ensure_ascii=False, indent=4)
