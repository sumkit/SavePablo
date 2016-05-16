"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from savepablo import views


urlpatterns = [ 
    url(r'^login$',auth_views.login,{'template_name':'login.html'},name='login'),
    url(r'^logout$',auth_views.logout_then_login,name='logout'),
    url(r'^register$',views.register,name='register'),
    url(r'^click$',views.click,name='click'),
    url(r'^mclick$',views.mclick,name='mclick'),
    url(r'^bought$', views.bought,name='bought'),
    url(r'^mbought$', views.mbought,name='mbought'),
    url(r'^load$',views.load,name='load'),
    url(r'^step$', views.step, name='step'),
    url(r'^mstep$', views.mstep, name='mstep'),
    url(r'^mHome$',views.mHome,name='mHome'),
    url(r'^queue$', views.queue,name='queue'),
    url(r'^ready$',views.ready,name='ready'),
    url(r'^game$',views.game,name='game'),
    url(r'^launch$',views.launch,name='launch'),
    url(r'^getopp$',views.getopp,name='getopp'),
    url(r'^cancel$',views.cancel,name='cancel'),
    url(r'^cancel2$',views.cancel2,name='cancel2'),
    url(r'^invite/(?P<id>[a-z0-9\-]+)$',views.invite,name='invite'),
    url(r'^link$',views.link,name='link'),
    url(r'^wait_accept$',views.waitAccept,name='waitAccept'),
    url(r'^unload$',views.unload,name='unload'),
    url(r'^$', views.home, name = 'home'),
    url(r'^getBoard$', views.getBoard, name='getBoard'),
    url(r'^getFam$', views.getFam, name='getFam'),
    url(r'^search$', views.search, name='search'),
    url(r'^debuff$',views.debuff,name='debuff'),
    url(r'^friend/(?P<id>\d+)$', views.friend, name='friend'),
    url(r'^unfriend/(?P<id>\d+)$', views.unfriend, name='unfriend'),
    url(r'^link2/(?P<id>\d+)$',views.link2,name='link2'),
    url(r'^congrats$', views.congrats, name='congrats'),
    url(r'^lose$', views.lose, name='lose'),
]
