## Week3 Assignment - News Search Engine

这是2018年THU程设小学期的第三周大作业 - 新闻搜索引擎

## 界面

![](https://raw.githubusercontent.com/xalanq/THU_Summer2018_Week3_Assignment/master/doc/img/index.png)

![](https://raw.githubusercontent.com/xalanq/THU_Summer2018_Week3_Assignment/master/doc/img/search.png)

![](https://raw.githubusercontent.com/xalanq/THU_Summer2018_Week3_Assignment/master/doc/img/post.png)

## 本机环境

* Python 3.7.0
* Django 2.1.1
* requests 2.19.1
* BeautifulSoup4 4.6.3
* [thulac](https://github.com/thunlp/THULAC-Python)

## 使用

首先使用`scaper`文件夹下的爬虫`scraper.py`对“人民网”、“新华网”的新闻进行爬取

```
python scraper.py
```

之后会将爬取的数据存储到`peaple.json`和`xinhua.json`中

然后在`web`文件夹下，运行

```
python manage.py makemigrations
python manage.py migrate
```

初始化数据库，然后再执行

```
python manage.py updateDB
```

将爬取的数据导入到数据库中（这可能会等很长时间），之后再执行

```
python manage.py updateRelation
```

更新文章推荐的数据库，最后

```
python manage.py runserver
```

启动服务器即可，你就可以通过`127.0.0.1:8000`进行访问网站了

目前的效率是，17000篇新闻的话，在i5-7200U的机子上查询新闻只要0.1s左右。（反正Django自带的sqlite有多快我这个就有多快）

## 开发文档

请移步[doc](/doc)文件夹

## 协议

Apache License 2.0