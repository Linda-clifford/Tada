import re
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from blog.models import Article  


def smart_split(text):
    # Step 1: Normalize white space
    text = re.sub(r'\s+', ' ', text).strip()

    # Step 2: Break after sentence endings before a capital letter
    text = re.sub(r'(?<=[.?!])\s+(?=[A-Z])', '\n\n', text)

    # Step 3: Add breaks before likely section headers or dates
    text = re.sub(r'\b(Timeline|Key Background|Topline|Followed|Following|Latest|Share to Facebook|Share to Twitter|Share to Linkedin)\b', r'\n\n\1', text)
    text = re.sub(r'(?<=\d{4}),?(?=\s?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))', r'\n\n', text)

    # Step 4: Add breaks before "+1 day ago" or similar
    text = re.sub(r'(\+\d+\s(day|hour|minute)s?\sago)', r'\n\n\1', text)

    # Step 5: Add spacing after em-dash (—) and colon if part of sentence
    text = re.sub(r'—', r' — ', text)
    text = re.sub(r':(?=\S)', r': ', text)

    return text



class Command(BaseCommand):
    help = "Cleans and formats full_content of articles"

    def handle(self, *args, **kwargs):
        articles = Article.objects.all()
        cleaned = 0

        for article in articles:
            raw = article.content
            if raw:
                soup = BeautifulSoup(raw, "html.parser")
                paragraphs = soup.find_all("p")

                if paragraphs:
                    cleaned_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs)
                else:
                    # Fallback for plain text (likely jam-packed ones)
                    cleaned_text = soup.get_text(separator=" ", strip=True)
                    cleaned_text = smart_split(cleaned_text)

                if cleaned_text and cleaned_text != article.full_content:
                    article.content = cleaned_text
                    article.save()
                    cleaned += 1

        self.stdout.write(self.style.SUCCESS(f"{cleaned} articles cleaned and formatted with spacing."))
