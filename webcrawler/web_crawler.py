import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pymongo import MongoClient
import mysql.connector
import redis
import threading


mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["web_crawler"]
mongo_cache = mongo_db["html_cache"]


# To not hardcode, created env file with the variables
mysql_connection = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="web_crawler"
)
cursor = mysql_connection.cursor()



cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS scraped_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url TEXT NOT NULL,
        title TEXT,
        meta_description TEXT
    )
    """
)

# Redis setup for queue and visited links
redis_client = redis.Redis(host="localhost", port=6379, db=0)


class HeadlessBrowser:
    def __init__(self):
        from mechanicalsoup import StatefulBrowser
        self.browser = StatefulBrowser()

    def fetch_html(self, url):
        try:
            self.browser.open(url)
            return self.browser.get_current_page()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
browser_instance = HeadlessBrowser()

lock = threading.Lock()

def scrape_links(url):
    html = browser_instance.fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(str(html), "html.parser")
    a_tags = soup.find_all("a")
    hrefs = [a.get("href") for a in a_tags]
    wikipedia_domain = "https://en.wikipedia.org"
    new_links = []

    for href in hrefs:
        if href and filter_link(href):
            new_links.append(urljoin(wikipedia_domain, href))

    return new_links



def filter_link(href):
    return (
        href.startswith("/wiki/") and
        "Help:" not in href and
        "Special:" not in href and
        "Wikipedia:" not in href and
        "Portal:" not in href and
        "Category:" not in href and
        href != "/wiki/Main_Page"
    )

def scrape_data(url):
    """Extract structured data from HTML and store it in MySQL."""
    html = browser_instance.fetch_html(url)
    if not html:
        return

    soup = BeautifulSoup(str(html), "html.parser")
    title = soup.title.string if soup.title else None
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag["content"] if meta_desc_tag else None

    cursor.execute(
        "INSERT INTO scraped_data (url, title, meta_description) VALUES (%s, %s, %s)",
        (url, title, meta_description)
    )
    mysql_connection.commit()



def crawl():
    """Core crawl loop pulling tasks from Redis."""
    while True:
        link = redis_client.lpop("links")
        if not link:
            break

        link = link.decode("utf-8")
        with lock:
            if redis_client.hexists("visited", link):
                continue
            redis_client.hset("visited", link, 1)

        print(f"Crawling: {link}")
        scrape_data(link)
        new_links = scrape_links(link)
        for new_link in new_links:
            redis_client.rpush("links", new_link)





def start_crawler(start_url, num_threads=4):
    """Start the crawler with multithreading."""
    redis_client.rpush("links", start_url)

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=crawl)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()










if __name__ == "__main__":
    start_url = "https://en.wikipedia.org/wiki/Redis"
    start_crawler(start_url, num_threads=4)





    cursor.close()
    mysql_connection.close()
    mongo_client.close()
