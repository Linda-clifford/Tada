import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils.text import slugify
from django.utils.timezone import now
from datetime import datetime
from .models import Article

# Add domain-specific selectors here
DOMAIN_SELECTORS = {
    "www.forbes.com": ["div.article-body", "div.content-body"],
    "www.politico.com": ["div.story-text"],
    "www.bloomberg.com": ["section.paywall-article-body"],
    # Add other known domains
}

def get_content_selector(url, soup):
    """
    Determines the appropriate selector for a given URL and extracts the content.

    :param url: The article URL
    :param soup: BeautifulSoup object of the parsed HTML
    :return: Extracted content or None
    """
    domain = urlparse(url).netloc
    selectors = DOMAIN_SELECTORS.get(domain, [])
    for selector in selectors:
        content = soup.select_one(selector)
        if content:
            return content.get_text(strip=True)
    return None


def detect_source(url):
    """
    Detects the source based on the URL domain.
    """
    domain = urlparse(url).netloc.lower()
    if 'techcrunch' in domain:
        return 'TechCrunch'
    elif 'engadget' in domain:
        return 'Engadget'
    elif 'theverge' in domain:
        return 'The Verge'
    else:
        return 'Unknown'


def fetch_and_store_articles():
    url = 'https://newsapi.org/v2/everything?q=apple&from=2025-04-24&to=2025-04-24&sortBy=popularity&apiKey=' + settings.NEWS_API_KEY
    response = requests.get(url)

    if response.status_code == 200:
        articles = response.json().get('articles', [])
        for article in articles:
            try:
                title = article.get('title', '').strip()
                published_at = article.get('publishedAt', '').strip()

                if not title or title.lower() == 'untitled':
                    print(f"Skipping article with invalid title: '{title}'")
                    continue

                if not published_at:
                    print(f"Skipping article with missing published date: '{title}'")
                    continue

                pub_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

                if Article.objects.filter(title=title, published_at=pub_date).exists():
                    print(f"Skipping duplicate article: '{title}' ({pub_date})")
                    continue

                slug = slugify(title)

                # Assign source based on URL
                article_url = article['url']
                if 'techcrunch.com' in article_url:
                    source = 'TechCrunch'
                elif 'cnn.com' in article_url:
                    source = 'CNN Tech'
                elif 'engadget.com' in article_url:
                    source = 'Engadget'
                elif 'theverge.com' in article_url:
                    source = 'The Verge'
                else:
                    source = None  # Unknown

                Article.objects.create(
                    url=article_url,
                    title=title,
                    slug=slug,
                    author=article.get('author', 'Unknown'),
                    description=article.get('description', ''),
                    content=article.get('content', ''),
                    image_url=article.get('urlToImage', ''),
                    published_at=pub_date,
                    source=source, 
                    status='draft',
                )

                print(f"Article '{title}' saved.")

            except Exception as e:
                error_message = f"{datetime.now()} - Error saving article '{article.get('title', 'Unknown')}': {e}"
                print(error_message)
                with open("article_save_errors.log", "a") as log_file:
                    log_file.write(error_message + "\n")
    else:
        print(f"Error fetching articles: {response.status_code}")
