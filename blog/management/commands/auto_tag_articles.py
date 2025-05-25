from django.core.management.base import BaseCommand
from blog.models import Article, Tag

class Command(BaseCommand):
    help = 'Automatically assign tags to articles based on keywords'

    def handle(self, *args, **kwargs):
        keywords_to_tags = {
            'AI': 'AI',
            'artificial intelligence': 'AI',
            'Apple': 'Apple',
            'iPhone': 'iPhone',
            'iOS': 'iPhone',
            'Android': 'Android',
            'Microsoft': 'Microsoft',
            'Google': 'Google',
            'cybersecurity': 'Cybersecurity',
            'hack': 'Cybersecurity',
            'breach': 'Cybersecurity',
            'cloud': 'Cloud',
            'machine learning': 'Machine Learning',
            'design': 'Design',
            'social media': 'Social Media',
            'gadget': 'Gadgets',
            'review': 'Reviews',
            'space': 'Space',
            'science': 'Science',
            'innovation': 'Innovation',
            'wearables': 'Wearables',
            'VR / AR': 'Tech News'

        }

        # Load all tags into a dictionary
        tag_objects = {tag.name: tag for tag in Tag.objects.all()}

        articles = Article.objects.all()
        total_tagged = 0

        for article in articles:
            matched_tags = set()

            text = f"{article.title} {article.description} {article.full_content}".lower()

            for keyword, tag_name in keywords_to_tags.items():
                if keyword.lower() in text:
                    tag = tag_objects.get(tag_name)
                    if tag:
                        matched_tags.add(tag)

            if matched_tags:
                article.tags.add(*matched_tags)
                total_tagged += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully auto-tagged {total_tagged} articles!'))
