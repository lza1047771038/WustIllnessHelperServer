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
    url(r'^Update/UserCoin', views.UpdateUserCoin),
    url(r'^Upload/SchoolImages', views.uploadSchoolImage),
    url(r'^Upload/Images', views.themeImageUpload),
    url(r'^Upload/Files', views.uploadFiles),
    url(r'^Search', views.Search),
    url(r'^Request/Theme', views.Theme_Response),
    url(r'^Request/Comments', views.Comment_Response),
    url(r'^Request/Reply', views.reply_response),
    url(r'^Request/SubjectHomeWork', views.SubjectHomeWorkRequest),
    url(r'^Request/SubjectComment', views.SubjectCommentRequest),
    url(r'^Request/Subjects', views.SubjectsRequest),
    url(r'^Request/ClassSection', views.ClassSectionRequest),
    url(r'^Request/SurveyResult', views.Survey_result),
    url(r'^Request/SurveyList', views.Survey_List),
    url(r'^Request/SurveyInfo', views.Survey_Response),
    url(r'^Request/NotificationDetails', views.NotificationDetails),
    url(r'^Request/queryForUserInfo', views.queryForUserInfo),
    url(r'^Request/NotificationList', views.NotificationList),
    url(r'^Post/Notification', views.NotificationPost),
    url(r'^Post/Theme', views.post_themes),
    url(r'^Post/Comment', views.post_comments),
    url(r'^Post/Reply', views.post_replies),
    url(r'^Post/Subjects', views.SubjectsPost),
    url(r'^Post/SubjectComment', views.SubjectCommentPost),
    url(r'^Post/SubjectHomeWork', views.SubjectHomeWorkPost),
    url(r'^Post/ClassSection', views.ClassSectionPost),
    url(r'^Delete/Subject', views.SubjectDelete),
    url(r'^MediaFiles/mediaImages/(?P<path>(.+))/$', views.Img_Get),
    url(r'^MediaFiles/SurveyResult/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^MediaFiles/CBTClassFiles/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^AddSingleQuestion', views.Survey_SingleQuestion_Save),
    url(r'^AddMutipleQuestion', views.Survey_MutipleQuestion_Save),
    url(r'^AddManualQuestion', views.Survey_ManualQuestion_Save),
    url(r'^AddSurveyInfos', views.Survey_save),
]

urlpatterns += staticfiles_urlpatterns()
