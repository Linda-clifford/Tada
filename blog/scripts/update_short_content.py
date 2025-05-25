import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from blog.models import Article

# Optionally import newspaper3k if you choose to use it
# from newspaper import Article as NewsArticle


def scrape_full_content(url):
    domain = urlparse(url).netloc
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Site-specific scraping logic
        if 'cnn.com' in domain:
            content = soup.find('div', class_='article__content')
        elif 'bbc.com' in domain:
            content = soup.find('article')
        elif 'aljazeera.com' in domain:
            content = soup.find('div', class_='wysiwyg wysiwyg--all-content css-1ck9wyi')
        else:
            content = soup.find('body')  # fallback

        if content:
            return content.get_text(separator='\n').strip()
    except Exception as e:
        print(f"[ERROR] Exception scraping {url}: {e}")
    return None


def scrape_and_update_article(article):
    print(f"Scraping: {article.title} - {article.url}")

    full_text = scrape_full_content(article.url)

    # Check for truncation artifacts
    if full_text and '[+123 chars]' in full_text:
        print(f"[WARN] Truncated content detected for {article.url}")
        full_text = scrape_full_content(article.url)  # Retry scraping

    if not full_text:
        print(f"[ERROR] Failed to extract full content for {article.title} ({article.url})")
    else:
        article.full_content = full_text
        article.save()
        print(f"[OK] Article updated: {article.title}")

