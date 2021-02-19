from django.contrib import admin

from .models import Article, Category


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_date', 'category']
    fields = ['title', 'content', 'created_date', 'category']


admin.site.register(Article, ArticleAdmin)
admin.site.register(Category)
