from django.core.management.base import BaseCommand
from blog.models import Article
from blog.scripts.scrape_articles import scrape_and_save_full_content

class Command(BaseCommand):
    help = 'Scrape all articles and update full content in the content field'

    def handle(self, *args, **kwargs):
        articles = Article.objects.filter(content__contains='[+')
        for article in articles:
            self.stdout.write(f"Scraping: {article.title}")
            success = scrape_and_save_full_content(article.id)
            if success:
                self.stdout.write(self.style.SUCCESS(f"✔ Updated: {article.title}"))
            else:
                self.stdout.write(self.style.ERROR(f"✖ Failed: {article.title}"))
