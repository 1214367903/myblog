from django.urls import include, path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    # 注意,blog_info是访问不了的,放这里只是占一个命名空间
    path('blog_info', views.blog_info, name='blog_info'),
    path('category/<str:name>', views.category, name='category'),
    path('article/<int:pk>', views.detail, name='detail'),
    path('search', include('haystack.urls'), name='search'),
]
