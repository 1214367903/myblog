from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'blog'
    verbose_name = '博客'

    def ready(self):
        from .cache import (on_article_init,
                            on_article_save,
                            on_article_delete)
