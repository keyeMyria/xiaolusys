#-*- coding:utf8 -*-
import json
import datetime
from .models import SaleTrade,SaleOrder,SaleRefund, FLASH_SELLER_ID
from shopback.base.service import LocalService
from shopback import paramconfig as pcfg
from common.utils import update_model_fields
from shopapp.weixin.models import MIAOSHA_SELLER_ID
from shopback.users.models import User
import logging

logger = logging.getLogger('celery.handler')

class FlashSaleService(LocalService):
    
    trade = None    
        
    def __init__(self,t):
        
        assert t not in ('',None)
        if isinstance(t,SaleTrade):
            self.trade = t
        else:
            self.trade = SaleTrade.objects.get(tid=t)
 
        
    @classmethod
    def createMergeOrder(cls,merge_trade,order,*args,**kwargs):
        
        from shopback.trades.models import MergeOrder
        from shopback.items.models import Product,ProductSku
        
        order_id = order.oid
        merge_order,state = MergeOrder.objects.get_or_create(oid=order_id,
                                                             merge_trade=merge_trade)
        state = state or not merge_order.sys_status
        
        if (order.status in (SaleOrder.TRADE_CLOSED,
                             SaleOrder.TRADE_CLOSED_BY_SYS) or 
            merge_trade.status == pcfg.TRADE_CLOSED or 
            merge_trade.status == SaleTrade.TRADE_CLOSED_BY_SYS):
            sys_status = pcfg.INVALID_STATUS
        else:
            sys_status = merge_order.sys_status or pcfg.IN_EFFECT
        
        if state:
            product = Product.objects.get(id=order.item_id)
            sku     = ProductSku.objects.get(id=order.sku_id,product=product)
              
            merge_order.payment = order.payment
            merge_order.total_fee = order.total_fee
            
            merge_order.num     = order.num
            merge_order.title   = order.title
            merge_order.outer_id      = product.outer_id
            merge_order.sku_properties_name = order.sku_name
            merge_order.outer_sku_id  = sku.outer_id
            
        merge_order.created  = merge_trade.created
        merge_order.pay_time = merge_trade.pay_time
        merge_order.status   = merge_trade.status
        merge_order.sys_status = sys_status
        merge_order.refund_fee    = order.refund_fee
        merge_order.refund_status = dict(SaleRefund.REFUND_STATUS_MAP).get(order.refund_status)
        merge_order.save()
        return merge_order
        
    @classmethod
    def getOrCreateSeller(cls,trade):
        
        seller_id = FLASH_SELLER_ID
        seller_type = User.SHOP_TYPE_WX
        for order in trade.normal_orders:
            if order.title.find(u'秒杀') >= 0:
                ###需要创建wxmiaosha 该买家才能正常工作
                seller_id   = MIAOSHA_SELLER_ID
                seller_type = User.SHOP_TYPE_SALE
                if trade.buyer_nick.find(u'[秒杀]') < 0:
                    trade.buyer_nick = u'[秒杀]' + trade.buyer_nick 
                break
        seller = User.getOrCreateSeller(seller_id,seller_type=seller_type)
        return seller
        
    @classmethod
    def createMergeTrade(cls,trade,*args,**kwargs):
        
        from shopback.trades.handlers import trade_handler 
        from shopback.trades.models import MergeTrade
        
        seller = cls.getOrCreateSeller(trade)
        merge_trade,state = MergeTrade.objects.get_or_create(tid=trade.tid,
                                                             user=seller)
        
        update_fields = ['buyer_nick','created','pay_time','modified','status']

        merge_trade.buyer_nick = trade.buyer_nick.strip() or trade.receiver_mobile
        
        merge_trade.created  = trade.created
        merge_trade.modified = trade.modified
        merge_trade.pay_time = trade.pay_time
        merge_trade.status   = SaleTrade.mapTradeStatus(trade.status) 
        
        update_address = False
        if not merge_trade.receiver_name and trade.receiver_name:
            update_address  = True
            address_fields = ['receiver_name','receiver_state',
                             'receiver_city','receiver_address',
                             'receiver_district','receiver_mobile',
                             'receiver_phone']
            
            for k in address_fields:
                setattr(merge_trade,k,getattr(trade,k))
            
            update_fields.extend(address_fields)
            
        merge_trade.payment      = merge_trade.payment or float(trade.payment)
        merge_trade.total_fee    = merge_trade.total_fee or float(trade.total_fee)
        merge_trade.post_fee     = merge_trade.post_fee or float(trade.post_fee)
        
        merge_trade.trade_from    = 0
        merge_trade.shipping_type = pcfg.EXPRESS_SHIPPING_TYPE
        merge_trade.type          = pcfg.SALE_TYPE

        update_model_fields(merge_trade,update_fields=update_fields
                            +['shipping_type','type','payment',
                              'total_fee','post_fee','trade_from'])

        for order in trade.sale_orders.all():
            cls.createMergeOrder(merge_trade,order)
        
        trade_handler.proccess(merge_trade,
                               **{'origin_trade':trade,
                                  'update_address':(update_address and 
                                                    merge_trade.status == pcfg.WAIT_SELLER_SEND_GOODS),
                                  'first_pay_load':(
                                    merge_trade.sys_status == pcfg.EMPTY_STATUS and 
                                    merge_trade.status == pcfg.WAIT_SELLER_SEND_GOODS)})
        
        return merge_trade
    
    
    def payTrade(self,*args,**kwargs):
        
        ########################## 押金链接，不需仓库处理 ######################
        outer_ids = set([o[0] for o in self.trade.normal_orders.values_list('outer_id')])
        if len(outer_ids) == 1 and list(outer_ids)[0].startswith('RMB'):
            return 
        ###################################################################
        
        return self.__class__.createMergeTrade(self.trade)
    
    
    def sendTrade(self,company_code=None,out_sid=None,retry_times=3,*args,**kwargs):
        
        from shopback.logistics.models import LogisticsCompany
        try:
            if not company_code:
                lg =  LogisticsCompany.getNoPostCompany()
            else:
                lg = LogisticsCompany.objects.get(code=company_code)
            self.trade.logistics_company = lg
            self.trade.out_sid = out_sid
            self.trade.consign_time      = datetime.datetime.now()
            self.trade.status  = SaleTrade.WAIT_BUYER_CONFIRM_GOODS
            self.trade.save()
            
            for order in self.trade.sale_orders.all():
                order.consign_time  = datetime.datetime.now()
                order.status  = SaleOrder.WAIT_BUYER_CONFIRM_GOODS
                order.save()
                
        except Exception,exc:
            logger.error(exc.message,exc_info=True)
        
        
