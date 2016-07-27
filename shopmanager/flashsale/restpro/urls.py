# coding: utf-8


from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from django.views.decorators.cache import cache_page
from rest_framework.urlpatterns import format_suffix_patterns

from rest_framework import routers
from . import views
from . import views_user
from . import views_product
from . import views_trade
from . import views_share
from . import views_coupon_new
from . import views_integral
from . import views_portal
from . import views_favorites
from flashsale.pay.views import weixin_login, weixin_test, weixin_auth_and_redirect
from flashsale.complain.views import ComplainViewSet
from flashsale.push import views as views_push

from . import views_wuliu
from . import views_praise
from . import views_pro_ref
from . import views_xlmm
from . import views_mmadver
from . import views_wuliu_new
from . import views_cushops
from . import views_promotion
from . import views_login_v2
from . import views_faqs
from . import views_mmexams

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'complain', ComplainViewSet)
router.register(r'register', views_user.RegisterViewSet)
router.register(r'users', views_user.CustomerViewSet)

router.register(r'posters', views_product.PosterViewSet)
router.register(r'products', views_product.ProductViewSet)
router.register(r'activitys', views_product.ActivityViewSet)
router.register(r'carts', views_trade.ShoppingCartViewSet)
router.register(r'favorites', views_favorites.FavoritesViewSet)
router.register(r'trades', views_trade.SaleTradeViewSet)
router.register(r'wxorders', views_trade.WXOrderViewSet)
router.register(r'portal', views_portal.PortalViewSet)
router.register(r'brands', views_portal.BrandEntryViewSet)


router.register(r'refunds', views.SaleRefundViewSet)
router.register(r'address', views.UserAddressViewSet)
router.register(r'districts', views.DistrictViewSet)
router.register(r'integral', views_integral.UserIntegralViewSet)
router.register(r'integrallog', views_integral.UserIntegralLogViewSet)
router.register(r'usercoupons', views_coupon_new.UserCouponsViewSet)
router.register(r'cpntmpl', views_coupon_new.CouponTemplateViewSet)

router.register(r'share', views_share.CustomShareViewSet)
router.register(r'saleproduct', views_praise.SaleProductViewSet)
router.register(r'hotproduct', views_praise.HotProductViewSet)
router.register(r'prorefrcd', views_pro_ref.ProRefRcdViewSet)
router.register(r'calcuprorefrcd', views_pro_ref.CalcuProRefRcd)
router.register(r'download', views.AppDownloadLinkViewSet)
router.register(r'faqs', views_faqs.SaleCategoryViewSet)
router.register(r'mmexam', views_mmexams.MmexamsViewSet)
router.register(r'mmwebviewconfig', views_mmadver.MamaVebViewConfViewSet)

#  推广接口注册
promotion_router = routers.DefaultRouter(trailing_slash=False)
promotion_router.register(r'xlmm', views_xlmm.XiaoluMamaViewSet)
promotion_router.register(r'carrylog', views_xlmm.CarryLogViewSet)
promotion_router.register(r'cashout', views_xlmm.CashOutViewSet)
# router.register(r'clickcount', views_xlmm.ClickCountViewSet)
promotion_router.register(r'shopping', views_xlmm.StatisticsShoppingViewSet)
promotion_router.register(r'mmadver', views_mmadver.XlmmAdvertisViewSet)
promotion_router.register(r'ninepic', views_mmadver.NinePicAdverViewSet)
promotion_router.register(r'cushop', views_cushops.CustomerShopsViewSet)
promotion_router.register(r'cushoppros', views_cushops.CuShopProsViewSet)
promotion_router.register(r'clicklog', views_xlmm.ClickViewSet)
promotion_router.register(r'free_proinfo', views_promotion.XLFreeSampleViewSet)
promotion_router.register(r'free_order', views_promotion.XLSampleOrderViewSet)
promotion_router.register(r'fanlist', views_promotion.InviteReletionshipView)

router.register(r'wuliu', views_wuliu_new.WuliuViewSet)

# 推送相关
router.register(r'push', views_push.PushViewSet)

router_urls = router.urls
router_urls_promotion = promotion_router.urls

router_urls += format_suffix_patterns([
    url(r'^users/weixin_login/$', weixin_login, name='weixin-login'),
    url(r'^users/weixin_test/$', weixin_test, name='weixin-test'),
    url(r'^users/weixin_auth/$', weixin_auth_and_redirect, name='xlmm-wxauth'),

    url(r'^products/modellist/(?P<model_id>[0-9]+)$',
        views_product.ProductViewSet.as_view({'get': 'modellist'}),
        name='product-model-list'),
    url(r'^products/preview_modellist/(?P<model_id>[0-9]+)$',
        views_product.ProductViewSet.as_view({'get': 'preview_modellist'}),
        name='product-model-list'),
    url(r'^products/(?P<pk>[0-9]+)/snapshot$',
        views_product.ProductShareView.as_view(),
        name='product-snapshot'),
    url(r'^brands/(?P<brand_id>[0-9]+)/products$',
        views_portal.BrandProductViewSet.as_view({'get': 'list'}),
        name='brand-product'),

    url(r'^trades/(?P<pk>[0-9]+)/orders$',
        views_trade.SaleOrderViewSet.as_view({'get': 'list'}),
        name='saletrade-saleorder'),
    url(r'^trades/(?P<pk>[0-9]+)/orders/details$',
        views_trade.SaleOrderViewSet.as_view({'get': 'details'}),
        name='saleorder-details'),
    url(r'^trades/(?P<tid>[0-9]+)/orders/(?P<pk>[0-9]+)$',
        views_trade.SaleOrderViewSet.as_view({'get': 'retrieve'}),
        name='saleorder-detail'),

    url(r'^order/(?P<pk>[0-9]+)/confirm_sign$',
        views_trade.SaleOrderViewSet.as_view({'post': 'confirm_sign'}),
        name='confirm_sign_order'),
    url(r'^users/integral',
        views_integral.UserIntegralViewSet.as_view({'get': 'list'}),
        name="user-intergral"),
    url(r'^users/integrallog',
        views_integral.UserIntegralLogViewSet.as_view({'get': 'list'}),
        name="user-intergrallog"),
    url(r'^users/(?P<pk>[0-9]+)/bang_budget',
        views_user.UserBugetBangView.as_view(),
        name="user-budget-bang"),
])

# 2016-3-2 v2
from flashsale.restpro.v2 import views_mama_v2, views_verifycode_login, views_packageskuitem
from flashsale.restpro.v2 import views_trade_v2, views_product_v2



v2_router = routers.DefaultRouter(trailing_slash=False)
v2_router.register(r'carts', views_trade_v2.ShoppingCartViewSet)
v2_router.register(r'products', views_product_v2.ProductViewSet)
v2_router.register(r'modelproducts', views_product_v2.ModelProductV2ViewSet)
v2_router.register(r'trades', views_trade_v2.SaleTradeViewSet)
v2_router.register(r'orders', views_trade_v2.SaleOrderViewSet)
v2_router.register(r'fortune', views_mama_v2.MamaFortuneViewSet)
v2_router.register(r'carry', views_mama_v2.CarryRecordViewSet)
v2_router.register(r'ordercarry', views_mama_v2.OrderCarryViewSet)
v2_router.register(r'awardcarry', views_mama_v2.AwardCarryViewSet)
v2_router.register(r'clickcarry', views_mama_v2.ClickCarryViewSet)
v2_router.register(r'activevalue', views_mama_v2.ActiveValueViewSet)
v2_router.register(r'referal', views_mama_v2.ReferalRelationshipViewSet)
v2_router.register(r'group', views_mama_v2.GroupRelationshipViewSet)
v2_router.register(r'visitor', views_mama_v2.UniqueVisitorViewSet)
v2_router.register(r'fans', views_mama_v2.XlmmFansViewSet)
v2_router.register(r'dailystats', views_mama_v2.DailyStatsViewSet)


v2_router.register(r'usercoupons', views_coupon_new.UserCouponsViewSet)
v2_router.register(r'cpntmpl', views_coupon_new.CouponTemplateViewSet)
v2_router.register(r'sharecoupon', views_coupon_new.OrderShareCouponViewSet)
v2_router.register(r'tmpsharecoupon', views_coupon_new.TmpShareCouponViewset)


v2_router_urls = v2_router.urls
v2_router_urls += ([

])


from flashsale.restpro.v2 import views_lesson
lesson_router = routers.DefaultRouter(trailing_slash=False)
lesson_router.register(r'lessontopic', views_lesson.LessonTopicViewSet)
lesson_router.register(r'lesson', views_lesson.LessonViewSet)
lesson_router.register(r'instructor', views_lesson.InstructorViewSet)
lesson_router.register(r'lessonattendrecord', views_lesson.LessonAttendRecordViewSet)

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="rest_base.html")),
    url(r'^v1/', include(router_urls, namespace='v1')),
    url(r'^v1/pmt/', include(router_urls_promotion, namespace='v1_promote')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^v2/', include(v2_router_urls, namespace='v2')),
    url(r'^v2/mama/', include(v2_router_urls, namespace='v2_mama')),
    url(r'^v2/mama/order_carry_visitor', views_mama_v2.OrderCarryVisitorView.as_view()),
    url(r'^v2/send_code', views_verifycode_login.SendCodeView.as_view()),
    url(r'^v2/verify_code', views_verifycode_login.VerifyCodeView.as_view()),
    url(r'^v2/reset_password', views_verifycode_login.ResetPasswordView.as_view()),
    url(r'^v2/passwordlogin', views_verifycode_login.PasswordLoginView.as_view()),
    url(r'^v2/weixinapplogin', views_verifycode_login.WeixinAppLoginView.as_view()),
    url(r'^v2/potential_fans', views_mama_v2.PotentialFansView.as_view()),                       
    url(r'^lesson/', include(lesson_router.urls, namespace='lesson')),
    url(r'^lesson/snsauth/', views_lesson.WeixinSNSAuthJoinView.as_view()),
    url(r'^packageskuitem', views_packageskuitem.PackageSkuItemView.as_view()),
)
