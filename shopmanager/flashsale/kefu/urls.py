# coding:utf-8
from django.conf.urls import url
from flashsale.kefu import views



urlpatterns = [
    url(r'^kefu_record/$', views.KefuRecordView.as_view(), name='searchProduct'),  # 搜索所有的商品 ajax

]
