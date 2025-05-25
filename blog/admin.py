from django.contrib import admin
from .models import Article, Comment, Tag

# Register your models here.




@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_at', 'featured')  # Show these columns
    list_filter = ('source', 'published_at', 'featured')  # Add filters on the right
    search_fields = ('title', 'source', 'author')  # Search bar for title, source, author
    prepopulated_fields = {'slug': ('title',)}  # Auto-generate slug from title

admin.site.register(Comment)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}