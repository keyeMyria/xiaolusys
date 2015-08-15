#-*- coding:utf-8 -*-
import time
import json
import datetime
from django.db import models
from django.shortcuts import get_object_or_404

from shopback.base.fields import BigIntegerAutoField,BigIntegerForeignKey
from shopback.logistics.models import LogisticsCompany
from shopback.items.models import DIPOSITE_CODE_PREFIX
from .models_user import Register,Customer
from .models_addr import District,UserAddress
from .models_custom import Productdetail,GoodShelf,ModelProduct
from .models_refund import SaleRefund
from .models_envelope import Envelop
from .models_coupon import Integral,IntegralLog,Coupon
from .managers import SaleTradeManager

from .signals import signal_saletrade_pay_confirm
from .options import uniqid
import uuid
from shopback.base import log_action, ADDITION, CHANGE

FLASH_SELLER_ID = 'flashsale'
AGENCY_DIPOSITE_CODE = DIPOSITE_CODE_PREFIX

def genUUID():
    return str(uuid.uuid1(clock_seq=True))

def genTradeUniqueid():
    return uniqid('%s%s'%(SaleTrade.PREFIX_NO,datetime.date.today().strftime('%y%m%d')))

class SaleTrade(models.Model):
    
    PREFIX_NO  = 'xd'
    WX_PUB     = 'wx_pub'
    ALIPAY_WAP = 'alipay_wap'
    UPMP_WAP   = 'upmp_wap'
    WALLET     = 'wallet'
    
    CHANNEL_CHOICES = (
        (WALLET,u'小鹿钱包'),
        (WX_PUB,u'微支付'),
        (ALIPAY_WAP,u'支付宝'),
        (UPMP_WAP,u'银联'),
    )
    
    PREPAY  = 0
    POSTPAY = 1
    
    TRADE_TYPE_CHOICES = (
        (PREPAY,u"在线支付"),
        (POSTPAY,"货到付款"),
    )
    
    TRADE_NO_CREATE_PAY = 0
    WAIT_BUYER_PAY = 1
    WAIT_SELLER_SEND_GOODS = 2
    WAIT_BUYER_CONFIRM_GOODS = 3
    TRADE_BUYER_SIGNED = 4
    TRADE_FINISHED = 5
    TRADE_CLOSED = 6
    TRADE_CLOSED_BY_SYS = 7
    
    NORMAL_TRADE_STATUS = (WAIT_BUYER_PAY,
                           WAIT_SELLER_SEND_GOODS,
                           WAIT_BUYER_CONFIRM_GOODS,
                           TRADE_BUYER_SIGNED,
                           TRADE_FINISHED,
                           TRADE_CLOSED,
                           TRADE_CLOSED_BY_SYS)
    
    REFUNDABLE_STATUS = (WAIT_SELLER_SEND_GOODS,
                         WAIT_BUYER_CONFIRM_GOODS)
    
    INGOOD_STATUS = (WAIT_SELLER_SEND_GOODS,
                     WAIT_BUYER_CONFIRM_GOODS,
                     TRADE_BUYER_SIGNED,
                     TRADE_FINISHED)
    
    TRADE_STATUS = (
        (TRADE_NO_CREATE_PAY,u'订单创建'),
        (WAIT_BUYER_PAY,u'待付款'),
        (WAIT_SELLER_SEND_GOODS,u'已付款'),
        (WAIT_BUYER_CONFIRM_GOODS,u'已发货'),
        (TRADE_BUYER_SIGNED,u'货到付款签收'),
        (TRADE_FINISHED,u'交易成功'),
        (TRADE_CLOSED,u'退款关闭'),
        (TRADE_CLOSED_BY_SYS,u'交易关闭'),
    )

    id    = BigIntegerAutoField(primary_key=True,verbose_name=u'订单ID')
    
    tid   = models.CharField(max_length=40,unique=True,
                             default=genTradeUniqueid,
                             verbose_name=u'原单ID')  
    buyer_id    = models.BigIntegerField(null=False,db_index=True,verbose_name=u'买家ID')
    buyer_nick  = models.CharField(max_length=64,blank=True,verbose_name=u'买家昵称')
    
    channel     = models.CharField(max_length=16,choices=CHANNEL_CHOICES,blank=True,verbose_name=u'付款类型')
    
    payment    =   models.FloatField(default=0.0,verbose_name=u'实付款')
    post_fee   =   models.FloatField(default=0.0,verbose_name=u'物流费用')
    discount_fee  =   models.FloatField(default=0.0,verbose_name=u'优惠折扣')
    total_fee  =   models.FloatField(default=0.0,verbose_name=u'总费用')
    
    buyer_message = models.TextField(max_length=1000,blank=True,verbose_name=u'买家留言')
    seller_memo   = models.TextField(max_length=1000,blank=True,verbose_name=u'卖家备注')
    
    created      = models.DateTimeField(null=True,auto_now_add=True,blank=True,verbose_name=u'生成日期')
    pay_time     = models.DateTimeField(db_index=True,null=True,blank=True,verbose_name=u'付款日期')
    modified     = models.DateTimeField(null=True,auto_now=True,blank=True,verbose_name=u'修改日期')
    consign_time = models.DateTimeField(null=True,blank=True,verbose_name=u'发货日期')
    
    trade_type = models.IntegerField(choices=TRADE_TYPE_CHOICES,default=PREPAY,verbose_name=u'订单类型')
    
    out_sid         = models.CharField(max_length=64,blank=True,verbose_name=u'物流编号')
    logistics_company  = models.ForeignKey(LogisticsCompany,null=True,
                                           blank=True,verbose_name=u'物流公司')
    receiver_name    =  models.CharField(max_length=25,
                                         blank=True,verbose_name=u'收货人姓名')
    receiver_state   =  models.CharField(max_length=16,blank=True,verbose_name=u'省')
    receiver_city    =  models.CharField(max_length=16,blank=True,verbose_name=u'市')
    receiver_district  =  models.CharField(max_length=16,blank=True,verbose_name=u'区')
    
    receiver_address   =  models.CharField(max_length=128,blank=True,verbose_name=u'详细地址')
    receiver_zip       =  models.CharField(max_length=10,blank=True,verbose_name=u'邮编')
    receiver_mobile    =  models.CharField(max_length=11,db_index=True,blank=True,verbose_name=u'手机')
    receiver_phone     =  models.CharField(max_length=20,blank=True,verbose_name=u'电话')

    openid  = models.CharField(max_length=40,blank=True,verbose_name=u'微信用户ID')
    charge  = models.CharField(max_length=28,verbose_name=u'支付编号')
    
    status  = models.IntegerField(choices=TRADE_STATUS,default=TRADE_NO_CREATE_PAY,
                              db_index=True,blank=True,verbose_name=u'交易状态')
    
    objects = models.Manager()
    normal_objects = SaleTradeManager()
    
    class Meta:
        db_table = 'flashsale_trade'
        verbose_name=u'特卖/订单'
        verbose_name_plural = u'特卖/订单列表'

    def __unicode__(self):
        return '<%s,%s>'%(str(self.id),self.buyer_nick)
    
    @property
    def normal_orders(self):
        return self.sale_orders.filter(status__in=SaleOrder.NORMAL_ORDER_STATUS)
    
    @property
    def order_title(self):
        if self.sale_orders.count() > 0:
            return self.sale_orders.all()[0].title
        return ''
    
    @property
    def order_num(self):
        onum = 0
        order_values = self.sale_orders.values_list('num')
        for order in order_values:
            onum += order[0]
        return onum
    
    @property
    def order_pic(self):
        if self.sale_orders.count() > 0:
            return self.sale_orders.all()[0].pic_path
        return ''
    
    @property
    def status_name(self):
        return self.get_status_display()
    
    @property
    def body_describe(self):
        subc = ''
        for order in self.sale_orders.all():
            subc += order.title
        return subc
    
    @property
    def order_buyer(self):
        return Customer.objects.get(id=self.buyer_id)
    
    @classmethod
    def mapTradeStatus(cls,index):
        from shopback.trades.models import MergeTrade
        status_list = MergeTrade.TAOBAO_TRADE_STATUS
        return status_list[index][0]
    
    def is_Deposite_Order(self):
        
        for order in self.sale_orders.all():
            if order.outer_id.startswith(AGENCY_DIPOSITE_CODE):
                return True
        return False
    
    def release_lock_skunum(self):
        try:
            for order in self.normal_orders:
                product_sku = ProductSku.objects.get(id=order.sku_id)
                Product.objects.releaseLockQuantity(product_sku, order.num)
        except Exception,exc:
            logger = logging.getLogger('django.request')
            logger.error(exc.message,exc_info=True)
    
    def confirm_payment(self):
        signal_saletrade_pay_confirm.send(sender=SaleTrade,obj=self)
            
    def charge_confirm(self,charge_time=None):
        
        self.status = self.WAIT_SELLER_SEND_GOODS
        self.pay_time = charge_time or datetime.datetime.now()
        self.save()
        
        for order in self.normal_orders:
            order.status = order.WAIT_SELLER_SEND_GOODS
            order.save()
        
        self.release_lock_skunum()        
        self.confirm_payment()
        
    def close_trade(self):
        """ 关闭待付款订单 """
        SaleTrade.objects.get(id=self.id,status=SaleTrade.WAIT_BUYER_PAY)
        
        for order in self.normal_orders:
            order.close_order()
            
        self.status = SaleTrade.TRADE_CLOSED_BY_SYS
        self.save()
            

class SaleOrder(models.Model):
    
    PREFIX_NO  = 'xo'
    TRADE_NO_CREATE_PAY = 0
    WAIT_BUYER_PAY = 1
    WAIT_SELLER_SEND_GOODS = 2
    WAIT_BUYER_CONFIRM_GOODS = 3
    TRADE_BUYER_SIGNED = 4
    TRADE_FINISHED = 5
    TRADE_CLOSED = 6
    TRADE_CLOSED_BY_SYS = 7

    ORDER_STATUS = (
        (TRADE_NO_CREATE_PAY,u'订单创建'),
        (WAIT_BUYER_PAY,u'待付款'),
        (WAIT_SELLER_SEND_GOODS,u'已付款'),
        (WAIT_BUYER_CONFIRM_GOODS,u'已发货'),
        (TRADE_BUYER_SIGNED,u'货到付款签收'),
        (TRADE_FINISHED,u'交易成功'),
        (TRADE_CLOSED,u'退款关闭'),
        (TRADE_CLOSED_BY_SYS,u'交易关闭'),
    )
    
    NORMAL_ORDER_STATUS = (WAIT_BUYER_PAY,
                           WAIT_SELLER_SEND_GOODS,
                           WAIT_BUYER_CONFIRM_GOODS,
                           TRADE_BUYER_SIGNED,
                           TRADE_FINISHED,)
    
    id    = BigIntegerAutoField(primary_key=True)
    oid   = models.CharField(max_length=40,unique=True,
                             default=lambda:uniqid('%s%s'%(SaleOrder.PREFIX_NO,datetime.date.today().strftime('%y%m%d'))),
                             verbose_name=u'原单ID')
    sale_trade = BigIntegerForeignKey(SaleTrade,related_name='sale_orders',
                                       verbose_name=u'所属订单')
    
    item_id  = models.CharField(max_length=64,blank=True,verbose_name=u'商品ID')
    title  =  models.CharField(max_length=128,blank=True,verbose_name=u'商品标题')
    price  = models.FloatField(default=0.0,verbose_name=u'商品单价')

    sku_id = models.CharField(max_length=20,blank=True,verbose_name=u'属性编码')
    num = models.IntegerField(null=True,default=0,verbose_name=u'商品数量')
    
    outer_id = models.CharField(max_length=64,blank=True,verbose_name=u'商品外部编码')
    outer_sku_id = models.CharField(max_length=20,blank=True,verbose_name=u'规格外部编码')
    
    total_fee    = models.FloatField(default=0.0,verbose_name=u'总费用')
    payment      = models.FloatField(default=0.0,verbose_name=u'实付款')

    sku_name = models.CharField(max_length=256,blank=True,
                                           verbose_name=u'购买规格')
    
    pic_path = models.CharField(max_length=512,blank=True,verbose_name=u'商品图片')
    
    created       =  models.DateTimeField(null=True,auto_now_add=True,blank=True,verbose_name=u'创建日期')
    modified      =  models.DateTimeField(null=True,auto_now=True,blank=True,verbose_name=u'修改日期')
    pay_time      =  models.DateTimeField(db_index=True,null=True,blank=True,verbose_name=u'付款日期')
    consign_time  =  models.DateTimeField(null=True,blank=True,verbose_name=u'发货日期')
    
    refund_id     = models.BigIntegerField(null=True,verbose_name=u'退款ID')
    refund_fee    = models.FloatField(default=0.0,verbose_name=u'退款费用')
    refund_status = models.IntegerField(choices=SaleRefund.REFUND_STATUS,
                                       default=SaleRefund.NO_REFUND,
                                       blank=True,verbose_name='退款状态')
    
    status = models.IntegerField(choices=ORDER_STATUS,default=TRADE_NO_CREATE_PAY,
                              db_index=True,blank=True,verbose_name=u'订单状态')

    class Meta:
        db_table = 'flashsale_order'
        verbose_name=u'特卖/订单明细'
        verbose_name_plural = u'特卖/订单明细列表'
        
    def __unicode__(self):
        return '<%s>'%(self.id)

    @property
    def refund(self):
        try:
            refund = SaleRefund.objects.get(trade_id=self.sale_trade.id,order_id=self.id)
            return refund
        except:
            return None
        
    @property
    def refundable(self):
        return self.sale_trade.status in SaleTrade.REFUNDABLE_STATUS
    
    def close_order(self):
        """ 待付款关闭订单 """
        try:
            SaleOrder.objects.get(id=self.id,status=SaleOrder.WAIT_BUYER_PAY)
        except SaleOrder.DoesNotExist,exc:
            return
    
        self.status = self.TRADE_CLOSED_BY_SYS
        self.save()
        sku = get_object_or_404(ProductSku, pk=self.sku_id)
        Product.objects.releaseLockQuantity(sku,self.num)
        

class TradeCharge(models.Model):
    
    order_no    = models.CharField(max_length=40,verbose_name=u'订单ID')
    charge      = models.CharField(max_length=28,verbose_name=u'支付编号')
    
    paid        = models.BooleanField(db_index=True,default=False,verbose_name=u'付款')
    refunded    = models.BooleanField(db_index=True,default=False,verbose_name=u'退款')
    
    channel     = models.CharField(max_length=16,blank=True,verbose_name=u'支付方式')
    amount      = models.CharField(max_length=10,blank=True,verbose_name=u'付款金额')
    currency    = models.CharField(max_length=8,blank=True,verbose_name=u'币种')
    
    transaction_no  = models.CharField(max_length=28,blank=True,verbose_name=u'事务NO')
    amount_refunded = models.CharField(max_length=16,blank=True,verbose_name=u'退款金额')
    
    failure_code    = models.CharField(max_length=16,blank=True,verbose_name=u'错误编码')
    failure_msg     = models.CharField(max_length=16,blank=True,verbose_name=u'错误信息')
    
#     out_trade_no    = models.CharField(max_length=32,db_index=True,blank=True,verbose_name=u'外部交易ID')
    
    time_paid       = models.DateTimeField(null=True,blank=True,db_index=True,verbose_name=u'付款时间')
    time_expire     = models.DateTimeField(null=True,blank=True,db_index=True,verbose_name=u'失效时间')
    
    class Meta:
        db_table = 'flashsale_trade_charge'
        unique_together = ("order_no","charge")
        verbose_name=u'特卖支付/交易'
        verbose_name_plural = u'特卖交易/支付列表'
        
    def __unicode__(self):
        return '<%s>'%(self.id)
    
from shopback.items.models import Product,ProductSku

class ShoppingCart(models.Model):
    """ 购物车 """
    
    NORMAL = 0
    CANCEL = 1
    
    STATUS_CHOICE = ((NORMAL,u'正常'),
                     (CANCEL,u'关闭'))
    
    id    = BigIntegerAutoField(primary_key=True)
    buyer_id    = models.BigIntegerField(null=False,db_index=True,verbose_name=u'买家ID')
    buyer_nick  = models.CharField(max_length=64,blank=True,verbose_name=u'买家昵称')
    
    item_id  = models.CharField(max_length=64,blank=True,verbose_name=u'商品ID')
    title  =  models.CharField(max_length=128,blank=True,verbose_name=u'商品标题')
    price  = models.FloatField(default=0.0,verbose_name=u'单价')

    sku_id = models.CharField(max_length=20,blank=True,verbose_name=u'属性编码')
    num = models.IntegerField(null=True,default=0,verbose_name=u'商品数量')
    
    total_fee    = models.FloatField(default=0.0,verbose_name=u'总费用')

    sku_name = models.CharField(max_length=256,blank=True, verbose_name=u'规格名称')
    
    pic_path = models.CharField(max_length=512,blank=True,verbose_name=u'商品图片')
    
    created       =  models.DateTimeField(null=True,auto_now_add=True,db_index=True,blank=True,verbose_name=u'创建日期')
    modified      =  models.DateTimeField(null=True,auto_now=True,db_index=True,blank=True,verbose_name=u'修改日期')
    remain_time   =  models.DateTimeField(null=True, blank=True, verbose_name=u'保留时间')

    status = models.IntegerField(choices=STATUS_CHOICE,default=NORMAL,
                              db_index=True,blank=True,verbose_name=u'订单状态') 
    
    class Meta:
        db_table = 'flashsale_shoppingcart'
        verbose_name=u'特卖/购物车'
        verbose_name_plural = u'特卖/购物车'
        
    def __unicode__(self):
        return '%s'%(self.id)
    
    def close_cart(self):
        """ 关闭购物车 """
        try:
            ShoppingCart.objects.get(id=self.id, status=ShoppingCart.NORMAL)
        except ShoppingCart.DoesNotExist:
            return
    
        self.status = self.CANCEL
        self.save()
        sku = get_object_or_404(ProductSku, pk=self.sku_id)
        Product.objects.releaseLockQuantity(sku,self.num)
    
    def std_sale_price(self):
        sku = ProductSku.objects.get(id=self.sku_id)
        return sku.std_sale_price
    
    def is_deposite(self):
        product = Product.objects.get(id=self.item_id)
        return product.outer_id.startswith('RMB')
    
    def is_good_enough(self):
        product_sku = ProductSku.objects.get(id=self.sku_id)
        return (product_sku.product.shelf_status == Product.UP_SHELF 
                and product_sku.real_remainnum >= self.num)
        
    def calc_discount_fee(self,xlmm=None):
        product_sku = ProductSku.objects.get(id=self.sku_id)
        return product_sku.calc_discount_fee(xlmm)
    
    
from signals_coupon import *

from shopback import signals

from django.contrib.auth.models import User as DjangoUser
def off_the_shelf_func(sender, product_list, *args, **kwargs):
    djuser, state = DjangoUser.objects.get_or_create(username='systemoa', is_active=True)
    for pro_bean in product_list:
        all_cart = ShoppingCart.objects.filter(item_id=pro_bean.id, status=ShoppingCart.NORMAL)
        for cart in all_cart:
            cart.close_cart()
            log_action(djuser.id, cart, CHANGE, u'下架后更新')
        all_trade = SaleTrade.objects.filter(sale_orders__item_id=pro_bean.id, status=SaleTrade.WAIT_BUYER_PAY)
        for trade in all_trade:
            trade.close_trade()
            log_action(djuser.id, trade, CHANGE, u'系统更新待付款状态到交易关闭')
        # SaleTrade.objects.filter(sale_orders__item_id=pro_bean.id, status=SaleTrade.WAIT_BUYER_PAY)\
        #     .update(status=SaleTrade.TRADE_CLOSED_BY_SYS)
        # SaleOrder.objects.filter(item_id=pro_bean.id, status=SaleOrder.WAIT_BUYER_PAY)\
        #     .update(status=SaleOrder.TRADE_CLOSED_BY_SYS)

signals.signal_product_downshelf.connect(off_the_shelf_func, sender=Product)

