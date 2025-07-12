from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Comment, Tag
from .utils import fetch_and_store_articles
from django.contrib import messages
from blog.scripts.scrape_articles import scrape_and_save_full_content
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from random import sample
from django.db.models import Q
from .forms import CommentForm, ContactForm
from random import sample
from django.http import Http404
from django.http import HttpResponseNotFound
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages


def home(request):
    #fetch_and_store_articles()
    articles_list = Article.objects.filter(status='published').order_by('-published_at')

    tags = Tag.objects.all()
    paginator = Paginator(articles_list, 6)  # Show 10 articles per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    featured_articles = list(Article.objects.filter(featured=True))
    latest_posts = sample(featured_articles, min(len(featured_articles),5)) 


    return render(request, 'blog/home.html', {
        'page_obj': page_obj,
        'latest_posts': latest_posts,
        'active_nav': 'latest',
        'tags': tags,
        "request": request,
        "show_ads": True
        })


def article_detail(request, slug):
    # Retrieve the article using the slug
    article = get_object_or_404(Article, slug=slug)
    #comments = article.comments.all().select_related('parent').prefetch_related('replies').order_by('created_at')
    comments = article.comments.filter(parent__isnull=True).prefetch_related('replies').order_by('created_at')

    related_articles = Article.objects.filter(
    tags__in=article.tags.all()
    ).exclude(id=article.id).distinct()

    # Convert to list for shuffling
    related_articles = list(related_articles)

    # Shuffle and limit to 3 if more than 3
    if len(related_articles) >= 3:
        related_articles = sample(related_articles, 3)


    # Check if the full content is already scraped
    if not article.content:
        try:
            # Trigger the scraping process
            success = scrape_and_save_full_content(article.id)
            if success:
                article.refresh_from_db()  # Refresh the article data after scraping
            else:
                messages.error(request, "Failed to scrape full content for this article.")
        except Exception as e:
            print(f"Error scraping content for article {article.slug}: {e}")
            messages.error(request, "An error occurred while scraping the article content.")

    # Comment form 
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            parent_id =request.POST.get('parent')
            if parent_id:
                parent_comment = Comment.objects.filter(id=parent_id).first()
                comment.parent = parent_comment
            comment.save()
            return redirect('article_detail', slug=slug)
    else:
        form = CommentForm()
    
    context = {
        'article': article,
        'comments': comments,
        'form': form,
        'related_articles': related_articles,
        "request": request,
        "show_ads": True,
    }

    # Pass the article data to the template
    return render(request, "blog/article_detail.html", context)




def source_articles(request, source):
    articles = Article.objects.filter(url__icontains=source).order_by('-published_at')

    tags = Tag.objects.all()

    paginator = Paginator(articles, 5)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)


    featured_articles = list(Article.objects.filter(featured=True))
    latest_posts = sample(featured_articles, min(len(featured_articles),7))


    return render(request, "blog/source_articles.html", {
        "page_obj": page_obj,
        "source": source,
        "active_nav": source,
        "request": request,
        "tags": tags,
        "latest_posts": latest_posts,
    })




def category_articles(request, category):
    articles = Article.objects.filter(
        Q(title__icontains=category) | Q(description__icontains=category)
    ).order_by('-published_at')

    tags = Tag.objects.all()

    paginator = Paginator(articles, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    featured_articles = list(Article.objects.filter(featured=True))
    latest_posts = sample(featured_articles, min(len(featured_articles),7)) 

    return render(request, "blog/category_articles.html", {
        "page_obj": page_obj,
        "category": category,
        "active_nav": category,
        "request": request,
        "tags": tags,
        "latest_posts": latest_posts,
    })

def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    articles = Article.objects.filter(tags=tag)
    paginator = Paginator(articles, 8)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/tag_detail.html', {
        'tag': tag,
        'articles': articles,
        'page_obj': page_obj,
        "request": request,
    })



def search_articles(request):
    query = request.GET.get('q')
    results = Article.objects.none()

    if query:
        results = Article.objects.filter(
            title__icontains=query
        ).order_by('-published_at')

    if not results.exists():
        return HttpResponseNotFound(render(request, 'blog/404.html'))

    paginator = Paginator(results, 6)
    page = request.GET.get('page')

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'query': query,
        'page_obj': page_obj,
    }

    return render(request, 'blog/search_results.html', context)

from django.core.mail import send_mail

def contact(request):
    form = ContactForm()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid() and request.POST.get('consent'):
            subject = f"New Contact Message from {form.cleaned_data['name']}"
            message = form.cleaned_data['message']
            sender = form.cleaned_data['email']  # user input
            recipient = settings.DEFAULT_FROM_EMAIL

            try:
                email = EmailMessage(
                    subject,
                    message,
                    from_email = recipient,
                    to = [recipient],
                    headers={'Reply-To': sender}  # when you click "Reply", it replies to the user's email
                )
                email.send(fail_silently=False)
                messages.success(request, "Your message was sent successfully!")
                return redirect('contact')
            except Exception as e:
                import traceback
                print("Zoho SMTP error:", traceback.format_exc())
                messages.error(request, "Oops! Something went wrong. Try again later.")

    return render(request, 'blog/contact.html', {'form': form})



def privacy_policy(request):
    return render(request, 'blog/privacy_policy.html')
