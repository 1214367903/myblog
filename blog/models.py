from django.db import models
from django.urls import reverse
from django.utils import timezone
from mdeditor.fields import MDTextField


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    class Meta:
        managed = True
        verbose_name = '类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'name': self.name})


class Article(models.Model):
    title = models.CharField('标题', max_length=100)
    content = MDTextField('正文')
    created_date = models.DateField('创建日期', default=timezone.now, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='分类')
    views = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        managed = True
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ['-created_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def viewed(self):
        # 注意,这个方法在并发环境可能出问题,最好加个锁(又不是重要数据,有必要吗???)
        self.views += 1
        self.save(update_fields=['views'])
