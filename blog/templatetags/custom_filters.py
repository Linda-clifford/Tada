from django import template
from django.utils import timezone

register = template.Library()


CATEGORY_KEYWORDS = {
    "Tech": ["technology", "AI", "robot", "startup", "software", "app"],
    "Health": ["health", "fitness", "doctor", "mental", "hospital", "medicine"],
    "Business": ["business", "finance", "market", "startup", "revenue", "stocks"],
    "Politics": ["government", "election", "senate", "policy", "president"],
    "Sports": ["football", "basketball", "olympics", "soccer", "match"],
}

@register.filter
def guess_category(article):
    text = (article.title + " " + article.description).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in text for word in keywords):
            return category
    return "General"

@register.filter(name='format_date')
def format_date(value):
    if isinstance(value, timezone.datetime):
        return value.strftime('%d %b %Y')  # Format: 07 Jun 2016
    return value
