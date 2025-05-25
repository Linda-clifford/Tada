from newspaper import Article
from blog.scripts.custom_scrapper import custom_scrape

def scrape_and_update_article(article_instance):
    try:
        article = Article(article_instance.url)
        article.download()
        article.parse()
        article_instance.full_content = article.text
        article_instance.save()
        print(f"[OK] Scraped with newspaper3k: {article_instance.url}")
    except Exception as e:
        print(f"[WARN] Newspaper3k failed for {article_instance.url}: {e}")
        try:
            content = custom_scrape(article_instance.url)
            article_instance.full_content = content
            article_instance.save()
            print(f"[OK] Scraped with fallback: {article_instance.url}")
        except Exception as fallback_error:
            print(f"[ERROR] Fallback scraper failed for {article_instance.url}: {fallback_error}")
