# MyBlog

**MyBlog**是一个极简风格的个人博客, 基于`python3.8`和`Django3.1`.

## 主要功能

- 文章支持markdown语法,前端代码高亮
- 支持文章的全文检索
- 文章页面自动生成目录和防盗水印
- 对查多改少的资源做了缓存,并通过信号量智能刷新
- 集成debug-toolbar,调试更轻松
- 网站异常邮件提醒

## 实例

[https://zeyuliu.xyz](https://zeyuliu.xyz)

## 部署

1. 搭建`python`环境,安装[requirements](requirements.txt)中的依赖
2. 在[settings](myblog/settings.py)中设置以下内容:
    - 你的`SECRET_KEY`
    - 在`ALLOWED_HOSTS`中加入你的网站域名
    - 你的`personal_info`和`RSS_INFO`
    - 你的邮箱配置
    - 数据库和缓存配置,默认是`mysql5.7`和`redis`
3. 让你的web server能够访问到项目的静态文件,包括`/static/`和`/media/`,它们的url和路径配置可以在[settings](myblog/settings.py)中找到
4. 运行[start.sh](start.sh),为了提高稳定性以及方便管理,推荐使用`supervisor`

## 注意事项

- 在DEBUG模式下,缓存自动关闭
- 本项目的缓存是基于django的信号量刷新的.因此,如果你通过django的ORM之外的方式操作数据库,就会造成缓存与数据库的数据不一致

## 使用许可

[MIT](LICENSE)
