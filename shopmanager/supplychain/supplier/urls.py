from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from django.views.decorators.csrf import csrf_exempt

from . import views, views_buyer_group


urlpatterns = [
    url(r'^brand/$', views.SaleSupplierList.as_view()),
    url(r'^brand/(?P<pk>[0-9]+)/$', views.SaleSupplierDetail.as_view()),
    url(r'^brand/charge/(?P<pk>[0-9]+)/$', views.chargeSupplier),

    url(r'^brand/fetch/(?P<pk>[0-9]+)/$', views.FetchAndCreateProduct.as_view()),

    url(r'^product/$', views.SaleProductList.as_view()),
    url(r'^line_product/$', views.SaleProductAdd.as_view()),
    url(r'^product/(?P<pk>[0-9]+)/$', views.SaleProductDetail.as_view()),
    url(r'^buyer_group/$', csrf_exempt(views_buyer_group.BuyerGroupSave.as_view())),
    url(r'^qiniu/$', views.QiniuApi.as_view()),
    # select sale_time
    url(r'^select_sale_time/$', views.change_Sale_Time),
]

urlpatterns = format_suffix_patterns(urlpatterns)