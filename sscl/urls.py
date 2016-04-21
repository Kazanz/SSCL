"""sscl URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from people import views as people_views
from sscl import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^clear/', views.clear, {}, 'clear'),
    url(r'^announcement/', views.announcement, {}, 'announcement'),
    url(r'^thank-you/', people_views.thank_you, {}, 'thank-you'),
    url(r'^confirm/(?P<hash>.*)/yes', people_views.confirm_yes, {}, 'confirm-yes'),
    url(r'^confirm/(?P<hash>.*)/', people_views.confirm, {}, 'confirm'),
    url(r'^send/', views.send_emails, {}, 'send'),
    url(r'^', people_views.waiver, {}, 'waiver'),
]
