"""
这个文件主要是为一些查多写少的资源做缓存,同时通过信号量自动更新缓存

浪费了几个小时得到结论:django的视图缓存真不好用,建议不要用
想要更新缓存的话,就得找到这个视图缓存的key,然后把对应的值删除
然而这个key你是不知道的,得通过get_cache_key传入一个request才能得到
所以你得伪造一个HttpRequest对象,这个对象的host,port,request_path等参数要和之前请求产生的缓存一致
但是你并不能得知django运行的Host,所以只好在启动时用socket获取本机的所有host,然后全部试一遍
而且这还没考虑到指定端口的情况
更离谱的是,如果url带参数,还找不到这个缓存
不管是get_absolute_url还是reverse都找不到,尚不确定django在缓存的时候给url做了什么手脚

由于cache的get,set等等操作带锁,本身就有原子性,而只是修改博客的话,并发量极低
因此,这里所有的操作都不带锁,不考虑线程安全问题,没必要
"""

from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import signals
from django.dispatch import receiver
from django.urls import reverse

from .models import Article


def view_wrapper(func):
    # 为装饰的视图函数进行缓存,假定视图函数的返回值只和path相关
    # 注意,这个函数会隐式地对中文url进行编码
    def wrapper(request, *args, **kwargs):
        key = f'blog:{quote(request.path)}'
        res = cache.get(key)
        if res is not None:
            return res
        res = func(request, *args, **kwargs)
        cache.set(key, res, timeout=None)
        return res

    # 这个函数不会在DEBUG模式下起作用,不然调试起来相当难受
    if settings.DEBUG:
        return func
    return wrapper


@receiver(signals.post_init, sender=Article)
def on_article_init(instance, **kwargs):
    instance.__original_title = instance.title
    # 其实按理来说,创建时间是不会变的,不然真的是wtf
    instance.__original_created_date = instance.created_date
    try:
        instance.__original_category = instance.category
    except ObjectDoesNotExist:
        # 如果是创建文章,还没来得及链接到分类,就会产生这个异常
        instance.__original_category = None


@receiver(signals.post_save, sender=Article)
def on_article_save(instance, created, **kwargs):
    if created:
        expire_view_cache(reverse('blog:index'))
        expire_view_cache(instance.category.get_absolute_url())
        return
    if instance.__original_category != instance.category:
        # 情景1,文章改分类,此时新旧分类的视图缓存失效,博客信息失效
        expire_view_cache(instance.category.get_absolute_url())
        expire_view_cache(instance.__original_category.get_absolute_url())
        expire_view_cache(reverse('blog:blog_info'))
    if instance.__original_title != instance.title or instance.__original_created_date != instance.created_date:
        # 情景2,标题或创建时间改变,此时主页和对应分类页缓存失效
        # 注意,这个情景和上一个不冲突
        expire_view_cache(reverse('blog:index'))
        expire_view_cache(instance.category.get_absolute_url())


@receiver(signals.post_delete, sender=Article)
def on_article_delete(instance, **kwargs):
    expire_view_cache(reverse('blog:index'))
    expire_view_cache(instance.category.get_absolute_url())
    expire_view_cache(reverse('blog:blog_info'))


def expire_view_cache(path) -> bool:
    return bool(cache.delete(f'blog:{path}'))
