import logging
import requests
import re  # <-- Added for cleaning truncation text
from blog.utils import get_content_selector
from datetime import datetime
from bs4 import BeautifulSoup
from blog.models import Article
from blog.playwright_scraper import fetch_content
from requests.exceptions import HTTPError

# Configure logging
logging.basicConfig(
    filename="scraping.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def scrape_and_save_full_content(article_id):
    """
    Scrapes an article and saves its full content into the database.
    """
    try:
        article = Article.objects.get(id=article_id)
        response = fetch_content(article.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Add fallback selectors for content containers
        content_container = (
            soup.select_one("section.m-component-detail") or
            soup.select_one("div.article-content") or
            soup.select_one("main.content") or
            soup.select_one("div.entry-content") or
            soup.select_one("article")
        )
        
        if not content_container:
            logging.error(f"Content container not found for article ID {article.id}, URL {article.url}")
            with open(f"debug_html_{article.id}.html", "w", encoding="utf-8") as debug_file:
                debug_file.write(soup.prettify())
            article.content = "Content extraction failed. Manual review required."
            article.save()
            return False
        
        # Extract and clean content
        raw_content = content_container.get_text(separator="\n", strip=True)
        cleaned_content = re.sub(r'\[\+\d+\schars\]', '', raw_content)

        # Save to database
        article.content = cleaned_content
        article.save()

        logging.info(f"Successfully scraped article ID {article_id} - URL: {article.url}")
        return True

    except Exception as e:
        logging.error(f"Error scraping article ID {article_id}, URL {article.url}: {e}")
        return False


def scrape_article(url):
    """
    Scrapes an article and extracts its main content using domain-specific selectors.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        content = get_content_selector(url, soup)
        if content:
            print(f"Content extracted for {url}:\n{content[:200]}...")
        else:
            print(f"No content found for {url}. Check the selectors.")
        return content

    except HTTPError as e:
        logging.error(f"HTTP error occurred for {url}: {e}")
        return None
    except Exception as e:
        logging.error(f"General error occurred for {url}: {e}")
        return None
