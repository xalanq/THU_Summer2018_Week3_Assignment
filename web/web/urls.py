"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.views.generic.base import RedirectView

from . import views

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    path('', views.index, name='index'),
    path('post', views.post_info, name='post_info'),
    path('s', views.search, name='search'),
    path('ajax_total', views.ajax_total, name='ajax_total'),
    path('ajax_index_category', views.ajax_index_category, name='ajax_index_category'),
    path('ajax_index_post', views.ajax_index_post, name='ajax_index_post'),
    path('ajax_search', views.ajax_search, name='ajax_search'),
    path('ajax_post_brief', views.ajax_post_brief, name='ajax_post_brief'),
    path('ajax_post_relation', views.ajax_post_relation, name='ajax_post_relation'),
    path('favicon.ico', favicon_view)
]
