from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',

#     (r'^supplier/',include('flashsale.supplier.urls')),
#     (r'^purchase/',include('flashsale.purchase.urls')),

#     (r'^pay/',include('flashsale.pay.urls')),
    (r'^complain/',include('flashsale.complain.urls')),
    (r'^dinghuo/',include('flashsale.dinghuo.urls')),
#     (r'^clickcount/', include('flashsale.clickcount.urls')),
    (r'^rebeta/',include('flashsale.clickrebeta.urls')),

    (r'^exam/',include('flashsale.mmexam.urls')),
    (r'^daystats/',include('flashsale.daystats.urls')),
    (r'^kefu/', include('flashsale.kefu.urls')),
    (r'^promotion/', include('flashsale.promotion.urls')),

)
