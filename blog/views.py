from collections import OrderedDict, namedtuple
from json import dumps

from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, render

from .cache import view_wrapper
from .models import Article, Category


@view_wrapper
def index(request):
    article_archive = OrderedDict()
    for article in Article.objects.all():
        year = article.created_date.year
        if year not in article_archive:
            article_archive[year] = []
        article_archive[year].append(article)
    return render(request, 'blog/index.html', context={
        'article_archive': article_archive,
    })


def detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.viewed()
    article.content = dumps(article.content)
    return render(request, 'blog/detail.html', context={'article': article})


@view_wrapper
def category(request, name):
    cate_obj = get_object_or_404(Category, name=name)
    articles = cate_obj.article_set.all()
    return render(request, 'blog/category.html', context={
        'articles': articles,
        'category': name
    })


@view_wrapper
def blog_info(_):
    # 返回博客信息,在模板中通过key名可获取对应的值
    category_count = Category.objects.annotate(Count('article')).filter(article__count__gt=0)
    category_item = namedtuple('category', ['name', 'link', 'number'])
    return {
        'all_categories': sorted(
            [category_item(cate.name, cate.get_absolute_url(), cate.article__count)._asdict() for cate in
             category_count], key=lambda x: -x['number']), }
