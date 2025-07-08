from .models import Article

def recent_articles_footer(request):
    try:
        articles = Article.objects.order_by('-published_at')[:2]
    except:
        articles = []
    return {'recent_footer_articles': articles}
