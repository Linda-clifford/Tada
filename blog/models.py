from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse

class Article(models.Model):

    SOURCE_CHOICES = [
        ('TechCrunch', 'TechCrunch'),
        ('Engadget', 'Engadget'),
        ('The Verge', 'The Verge'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    description = models.TextField()
    content = models.TextField(null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)
    image_urls = models.JSONField(default=list, blank=True)
    published_at = models.DateTimeField()
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    url = models.URLField(default='https://default.com', unique=True)
    featured = models.BooleanField(default=False)
    source = models.CharField(max_length=100,choices=SOURCE_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    tags = models.ManyToManyField('Tag', blank=True, related_name='articles')

    full_content = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

@receiver(post_save, sender=Article)
def auto_scrape_full_content(sender, instance, created, **kwargs):
    if created and not instance.content:
        from blog.scripts.update_full_content import scrape_and_update_article  # <--- moved import here
        scrape_and_update_article(instance)


class Comment(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    name = models.CharField(max_length=100)
    email = models.EmailField(null=False, blank=False, default='')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.name} on {self.article}'
    

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
