"""
TODO: 为缓存添加单元测试.
由于测试数据库与项目数据库不同,直接测试无法触发信号量,很多东西测不到
网上没找到解决方案,可能得研究源码自己解决了
虽然这部分我写得比较严谨,也手动测试了,但是最好加上单元测试
"""
from django.apps import apps
from django.test import TestCase
from django.urls import reverse

from .feeds import AllPostsRssFeed
from .models import Article, Category


class BasicTestCase(TestCase):
    # 这个类会自动创建数据,以及屏蔽全文索引的生成,做测试继承它就行了
    def setUp(self):
        apps.get_app_config('haystack').signal_processor.teardown()

        self.category1 = Category.objects.create(name='测试分类一')
        self.category2 = Category.objects.create(name='测试分类二')

        self.article1 = Article.objects.create(
            title='测试标题一',
            content='测试内容一',
            category=self.category1,
        )
        self.article2 = Article.objects.create(
            title='测试标题二',
            content='测试内容二',
            category=self.category2,
        )


class ArticleModelTestCase(BasicTestCase):

    def test_str_representation(self):
        self.assertEqual(self.article1.__str__(), self.article1.title)

    def test_get_absolute_url(self):
        expected_url = reverse('blog:detail', kwargs={'pk': self.article1.pk})
        self.assertEqual(self.article1.get_absolute_url(), expected_url)

    def test_increase_views(self):
        for _ in range(10):
            views = self.article1.views
            self.article1.viewed()
            self.article1.refresh_from_db()
            self.assertEqual(self.article1.views, views + 1)


class CategoryModelTestCase(BasicTestCase):

    def setUp(self):
        self.category1 = Category.objects.create(name='测试分类')

    def test_str_representation(self):
        self.assertEqual(self.category1.__str__(), self.category1.name)

    def test_get_absolute_url(self):
        expected_url = reverse('blog:category', kwargs={'name': self.category1.name})
        self.assertEqual(self.category1.get_absolute_url(), expected_url)


class IndexViewTestCase(BasicTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('blog:index')

    def test_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('blog/index.html')
        self.assertContains(response, self.article1.title)
        self.assertContains(response, self.article2.title)


class CategoryViewTestCase(BasicTestCase):
    def setUp(self):
        super().setUp()
        self.url = self.category1.get_absolute_url()

    def test_visit_a_nonexistent_category(self):
        url = reverse('blog:category', kwargs={'name': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('blog/detail.html')
        self.assertContains(response, self.article1.title)
        expected_qs = self.category1.article_set.all().order_by('-created_date')
        self.assertQuerysetEqual(response.context['articles'], [repr(p) for p in expected_qs])


class ArticleViewTestCase(BasicTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('blog:detail', kwargs={'pk': self.article1.pk})

    def test_visit_a_nonexistent_article(self):
        url = reverse('blog:detail', kwargs={'pk': 0})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_increase_views(self):
        for _ in range(10):
            views = self.article1.views
            self.client.get(self.url)
            self.article1.refresh_from_db()
            self.assertEqual(self.article1.views, views + 1)

    def test_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['article'], self.article1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('blog/detail.html')
        self.assertContains(response, self.article1.title)


class RSSTestCase(BasicTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('rss')

    def test_rss_subscription_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, AllPostsRssFeed.title)
        self.assertContains(response, AllPostsRssFeed.description)
        self.assertContains(response, self.article1.title)
        self.assertContains(response, self.article2.title)
        self.assertContains(response, f'[{self.article1.category}] {self.article1.title}')
        self.assertContains(response, f'[{self.article2.category}] {self.article2.title}')
