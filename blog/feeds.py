from django.conf import settings
from django.contrib.syndication.views import Feed

from .models import Article


class AllPostsRssFeed(Feed, settings.RSS_INFO):

    @staticmethod
    def items():
        return Article.objects.all()

    def item_title(self, item):
        return f'[{item.category}] {item.title}'

    def item_description(self, item):
        return ''
