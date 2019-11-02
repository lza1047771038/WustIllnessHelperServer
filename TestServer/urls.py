"""TestServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.views.static import serve

from TestServer import Search
from testserver_test import views
from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('searchform/', Search.search_form),
    path('search/', Search.search),
    url(r'^login', views.login),
    url(r'^register', views.Register),
    url(r'^update', views.UpdateInfo),
    url(r'^theme_request', views.Theme_Response),
    url(r'^comment_request', views.Comment_Response),
    url(r'^reply_request', views.reply_response),
    url(r'^theme_post', views.post_themes),
    url(r'^comment_post', views.post_comments),
    url(r'^reply_post', views.post_replies),
    url(r'^MediaFiles/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^Survey_Result', views.Survey_result),
    url(r'^Survey_List', views.Survey_List),
    url(r'^Survey_Response', views.Survey_Response),
    url(r'^AddSingleQuestion', views.Survey_SingleQuestion_Save),
    url(r'^AddMutipleQuestion', views.Survey_MutipleQuestion_Save),
    url(r'^AddManualQuestion', views.Survey_ManualQuestion_Save),
    url(r'^AddSurveyInfos', views.Survey_save),
    url(r'^ImagesUpload', views.themeImageUpload),
    url(r'^NotificationList', views.NotificationList),
    url(r'^NotificationPost', views.NotificationPost),
]

urlpatterns += staticfiles_urlpatterns()
