#-*- coding:utf-8 -*-
import time
import datetime
from django.db import models
from django.db.models import Q,Sum
from django.db.models.signals import post_save

from shopback import paramconfig as pcfg
from shopback.base.fields import BigIntegerAutoField,BigIntegerForeignKey
from .signals import signal_saletrade_refund_confirm
from .options import uniqid
from shopback.items.models import Product
from supplychain.supplier.models import SaleProduct
from shopback.base.models import JSONCharMyField


class SaleRefund(models.Model):
    
    NO_REFUND = 0
    REFUND_CLOSED = 1
    REFUND_REFUSE_BUYER = 2
    REFUND_WAIT_SELLER_AGREE = 3
    REFUND_WAIT_RETURN_GOODS = 4
    REFUND_CONFIRM_GOODS = 5
    REFUND_APPROVE = 6
    REFUND_SUCCESS = 7
    
    REFUND_STATUS = (
        (NO_REFUND,'没有退款'),
        (REFUND_WAIT_SELLER_AGREE,'买家已经申请退款'),
        (REFUND_WAIT_RETURN_GOODS,'卖家已经同意退款'),
        (REFUND_CONFIRM_GOODS,'买家已经退货'),
        (REFUND_REFUSE_BUYER,'卖家拒绝退款'),
        (REFUND_APPROVE,'确认退款，等待返款'),
        (REFUND_CLOSED,'退款关闭'),
        (REFUND_SUCCESS,'退款成功'),
    )
    
    REFUNDABLE_STATUS = (REFUND_WAIT_SELLER_AGREE,
                         REFUND_WAIT_RETURN_GOODS,
                         REFUND_CONFIRM_GOODS,
                         REFUND_APPROVE,
                         REFUND_SUCCESS)
    
    REFUND_STATUS_MAP = (
        (NO_REFUND,pcfg.NO_REFUND),
        (REFUND_WAIT_SELLER_AGREE,pcfg.REFUND_WAIT_SELLER_AGREE),
        (REFUND_WAIT_RETURN_GOODS,pcfg.REFUND_WAIT_RETURN_GOODS),
        (REFUND_CONFIRM_GOODS,pcfg.REFUND_CONFIRM_GOODS),
        (REFUND_REFUSE_BUYER,pcfg.REFUND_REFUSE_BUYER),
        (REFUND_APPROVE,pcfg.REFUND_SUCCESS),
        (REFUND_CLOSED,pcfg.REFUND_CLOSED),
        (REFUND_SUCCESS,pcfg.REFUND_SUCCESS)
    )
    
    BUYER_NOT_RECEIVED = 0
    BUYER_RECEIVED = 1
    BUYER_RETURNED_GOODS = 2
    
    GOOD_STATUS_CHOICES = (
        (BUYER_NOT_RECEIVED,'买家未收到货'),
        (BUYER_RECEIVED,'买家已收到货'),
        (BUYER_RETURNED_GOODS,'买家已退货'),
    )
    
    id           = BigIntegerAutoField(primary_key=True,verbose_name='ID')
    refund_no    = models.CharField(max_length=32,unique=True,
                                    default=lambda:uniqid('RF%s'%(datetime.datetime.now().strftime('%y%m%d'))),
                                    verbose_name='退款编号')
    trade_id     = models.IntegerField(verbose_name='交易ID')
    order_id     = models.IntegerField(verbose_name='订单ID')
    
    buyer_id    = models.BigIntegerField(db_index=True,default=0,verbose_name=u"客户ID")
    refund_id   = models.CharField(max_length=28,blank=True,db_index=True,verbose_name=u'P++退款编号')
    charge      = models.CharField(max_length=28,blank=True,db_index=True,verbose_name=u'P++支付编号')
    
    item_id      = models.BigIntegerField(null=True,default=0,verbose_name='商品ID')
    title        = models.CharField(max_length=64,blank=True,verbose_name='出售标题')
    
    sku_id       = models.BigIntegerField(null=True,default=0,verbose_name='规格ID')
    sku_name     = models.CharField(max_length=64,blank=True,verbose_name='规格标题')
    
    refund_num   = models.IntegerField(default=0,verbose_name='退货数量')
    
    buyer_nick   = models.CharField(max_length=64,blank=True,verbose_name='买家昵称')
    mobile = models.CharField(max_length=20,db_index=True,blank=True,verbose_name='手机')
    phone  = models.CharField(max_length=20,blank=True,verbose_name='固话')
    
    total_fee    = models.FloatField(default=0.0,verbose_name='总费用')
    payment      = models.FloatField(default=0.0,verbose_name='实付')
    refund_fee   = models.FloatField(default=0.0,verbose_name='退款费用')
    
    created   = models.DateTimeField(db_index=True,auto_now_add=True,verbose_name='创建日期')
    modified  = models.DateTimeField(auto_now=True,verbose_name='修改日期')

    company_name = models.CharField(max_length=64,blank=True,verbose_name='退回快递公司')
    sid       = models.CharField(max_length=64,db_index=True,blank=True,verbose_name='退回快递单号')

    reason = models.TextField(max_length=200, blank=True, verbose_name='退款原因')
    proof_pic = JSONCharMyField(max_length=10240, blank=True, null=True, verbose_name=u'佐证图片')
    desc = models.TextField(max_length=1000, blank=True, verbose_name='描述')
    feedback = models.TextField(max_length=1000, blank=True, verbose_name='审核意见')
    
    has_good_return = models.BooleanField(default=False,verbose_name='是否退货')
    has_good_change = models.BooleanField(default=False,verbose_name='是否换货')
    
    good_status  = models.IntegerField(db_index=True,choices=GOOD_STATUS_CHOICES,
                                    default=BUYER_RECEIVED,blank=True,verbose_name='退货商品状态')

    status       = models.IntegerField(db_index=True,choices=REFUND_STATUS,
                                    default=REFUND_WAIT_SELLER_AGREE,blank=True,verbose_name='退款状态')

    class Meta:
        db_table = 'flashsale_refund'
        unique_together = ("trade_id","order_id")
        verbose_name=u'特卖/退款单'
        verbose_name_plural = u'特卖/退款单列表'
        permissions = [("sale_refund_manage", u"特卖订单退款管理"),]
        
    def __unicode__(self):
        return '<%s>'%(self.id)
    
    def refund_desc(self):
        return u'退款(oid:%s),%s'%(self.order_id,self.reason)
    
    def get_tid(self):
        from flashsale.pay.models import SaleTrade
        strade = SaleTrade.objects.get(id=self.trade_id)
        return strade.tid
    
    def get_oid(self):
        from flashsale.pay.models import SaleOrder
        sorder = SaleOrder.objects.get(id=self.order_id)
        return sorder.oid
        
    def refund_Confirm(self):
        srefund = SaleRefund.objects.get(id=self.id)
        if srefund.status == SaleRefund.REFUND_SUCCESS:
            return

        self.status = SaleRefund.REFUND_SUCCESS
        self.save()
        from flashsale.pay.models import SaleOrder,SaleTrade
        sorder = SaleOrder.objects.get(id=self.order_id)
        sorder.refund_status = SaleRefund.REFUND_SUCCESS
        if sorder.status in (
            SaleTrade.WAIT_SELLER_SEND_GOODS,
            SaleTrade.WAIT_BUYER_CONFIRM_GOODS,
            SaleTrade.TRADE_BUYER_SIGNED):
            sorder.status = SaleTrade.TRADE_CLOSED
        sorder.save()
        
        strade = sorder.sale_trade
        if strade.normal_orders.count() == 0:
            strade.status = SaleTrade.TRADE_CLOSED
            strade.save()
        
        signal_saletrade_refund_confirm.send(sender=SaleRefund,obj=self)

    def pic_path(self):
        try:
            pro = Product.objects.get(id=self.item_id)
            return pro.pic_path
        except Product.DoesNotExist:
            return None

    def sale_contactor(self):
        """ 选品买手　"""
        try:
            pro = Product.objects.get(id=self.item_id)
            sal = SaleProduct.objects.get(id=pro.sale_product)
            return sal.contactor.id
        except:
            return None

    def pro_model(self):
        try:
            pro = Product.objects.get(id=self.item_id)
            return pro.model_id
        except Product.DoesNotExist:
            return None

    def outer_id(self):
        try:
            pro = Product.objects.get(id=self.item_id)
            return pro.outer_id
        except Product.DoesNotExist:
            return None

    def sale_order(self):
        from flashsale.pay.models import SaleOrder
        try:
            order = SaleOrder.objects.get(id=self.order_id)
        except SaleOrder.DoesNotExist:
            order = None
        return order


def buyeridPatch():
    
    from flashsale.pay.models import SaleTrade
    
    sfs = SaleRefund.objects.all()
    for sf in sfs:
        st = SaleTrade.objects.get(id=sf.trade_id)
        sf.buyer_id = st.buyer_id
        sf.save()
        

def handle_sale_refund_signal(sender,instance,*args,**kwargs):
    
    from .models import SaleTrade
    from shopback import signals
    from shopback.trades.models import MergeOrder

    strade = SaleTrade.objects.get(id=instance.trade_id)
    if (not strade.is_Deposite_Order() and 
        instance.status == SaleRefund.REFUND_WAIT_SELLER_AGREE):
        signals.order_refund_signal.send(sender=MergeOrder,obj=instance)

post_save.connect(handle_sale_refund_signal, sender=SaleRefund)

