"""
站点地图的作用是,你可以把它提交给搜索引擎,以此提升网站在搜索结果中的排名

谷歌的提交地址: https://search.google.com/search-console/about
"""

from django.contrib.sitemaps import Sitemap

from .models import Article


class ArticleSitemap(Sitemap):
    changefreq = 'monthly'
    priority = '0.6'

    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.created_date


sitemaps = {
    'article': ArticleSitemap,
}
