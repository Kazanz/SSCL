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
    url(r'^callback/', views.callback, {}, 'callback'),
    url(r'^thank-you/', people_views.thank_you, {}, 'thank-you'),
    url(r'^msg', people_views.msg, {}, 'confirm'),
    url(r'^confirm/(?P<hash>.*)/yes', people_views.confirm_yes, {}, 'confirm-yes'),
    url(r'^confirm/(?P<hash>.*)/no', people_views.confirm_no, {}, 'confirm-no'),
    url(r'^confirm/(?P<hash>.*)/', people_views.confirm, {}, 'confirm'),
    url(r'^sending-email/', people_views.sending_email, {}, 'sending-email'),
    url(r'^sending-text/', people_views.sending_text, {}, 'sending-text'),
    url(r'^unlock/', people_views.unlock, {}, 'unlock'),
    url(r'^send/', views.send_emails, {}, 'send'),
    url(r'^api/image/', views.image_update, {}, 'image'),
    url(r'^api/waivers/', views.waiver_data, {}, 'waiver-data'),
    url(r'^api/tracker/', views.tracker_data, {}, 'tracker-data'),
    url(r'^', people_views.waiver, {}, 'waiver'),
]
