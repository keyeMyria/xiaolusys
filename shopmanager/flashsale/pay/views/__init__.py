from .charge import PINGPPCallbackView, PayResultView, WXPayWarnView
from .envelop import EnvelopConfirmSendView
from .aggregate import AggregateProductView, ModelProductView, CheckModelExistView, \
    AggregateProductCheckView, ChuanTuAPIView, ModelChangeAPIView
from .login import flashsale_login, productlist_redirect, weixin_login, weixin_test, weixin_auth_and_redirect
from .address import AddressList, UserAddressDetail, DistrictList
from .refund import  RefundPopPageView, RefundReason, RefundAnaList
from .product import productsku_quantity_view, ProductDetailView
from .order import order_flashsale, time_rank, sale_state, refund_state, refunding_state, preorder_flashsale, \
    nextorder_flashsale, search_flashsale, change_sku_item, refund_fee, update_memo, sent_sku_item_again, get_mrgid
from .aggregate import AggregateProductView, ModelProductView, CheckModelExistView, \
    AggregateProductCheckView, ChuanTuAPIView, ModelChangeAPIView
from .poster import PostGoodShelf
from .zoneanalysis import show_Zone_Page, by_zone_Province, by_zone_City

from .extras import QiniuAPIView