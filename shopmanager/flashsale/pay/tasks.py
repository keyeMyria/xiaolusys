#-*- encoding:utf8 -*-
import time
import datetime
import calendar
from django.conf import settings
from django.db import models
from celery.task import task
from celery.task.sets import subtask
from django.conf import settings

from shopback.users.models import User
from shopapp.weixin.models import WeiXinUser,WeixinUnionID
from flashsale.pay.models import TradeCharge,SaleTrade,SaleOrder,SaleRefund,Customer
from .service import FlashSaleService
import logging

__author__ = 'meixqhi'

logger = logging.getLogger('celery.handler')


@task()
def task_Update_Sale_Customer(unionid,openid=None,app_key=None):
    
    if openid and app_key:
        WeixinUnionID.objects.get_or_create(openid=openid,app_key=app_key,unionid=unionid)
        
    try:
        profile, state = Customer.objects.get_or_create(unionid=unionid)
        
        wxuser = WeiXinUser.objects.get(models.Q(openid=openid)|models.Q(unionid=unionid))
        profile.nick   = wxuser.nickname
        profile.mobile = wxuser.mobile
        profile.openid = openid or profile.openid 
        profile.save()
            
    except Exception,exc:
        logger.debug(exc.message,exc_info=True)
    
from shopback.trades.models import MergeTrade,MergeBuyerTrade

  
@task()
def task_Push_SaleTrade_Finished(pre_days=10):
    """ 定时将待确认状态小鹿特卖订单更新成已完成 """
    
    day_date = datetime.datetime.now() - datetime.timedelta(days=pre_days)
    strades = SaleTrade.objects.filter(status=SaleTrade.WAIT_BUYER_CONFIRM_GOODS)
    for strade in strades:
        mtrades = MergeTrade.objects.filter(tid=strade.tid,type=MergeTrade.SALE_TYPE)
        if mtrades.count() == 0:
            continue
        
        mtrade = mtrades[0]
        if (mtrade.status == MergeTrade.TRADE_CLOSED or 
            mtrade.sys_status in (MergeTrade.INVALID_STATUS,MergeTrade.EMPTY_STATUS)):
            strade.status =  SaleTrade.TRADE_CLOSED
            strade.save()
        
        elif (mtrade.sys_status == MergeTrade.FINISHED_STATUS ):
            if mtrade.weight_time and mtrade.weight_time > day_date:
                continue
            
            #如果父订单已称重，并且称重日期达到确认期，则系统自动将订单放入已完成
            if not mtrade.weight_time :
                merge_status = MergeBuyerTrade.getMergeType(mtrade.id)
                if merge_status != MergeBuyerTrade.SUB_MERGE_TYPE:
                    continue
                smergetrade = MergeBuyerTrade.objects.get(sub_tid=mtrade.id)
                ptrade = MergeTrade.objects.get(id=smergetrade.main_tid)
                if not ptrade.weight_time or ptrade.weight_time > day_date:
                    continue
            
            sale_refunds = SaleRefund.objects.filter(trade_id=mtrade.id,status__gt=SaleRefund.REFUND_CLOSED)
            if sale_refunds.count() > 0:
                continue
            
            strade.status =  SaleTrade.TRADE_FINISHED
            strade.save()


@task(max_retry=3,default_retry_delay=60)
def confirmTradeChargeTask(sale_trade_id,charge_time=None):
    
    try:
        strade = SaleTrade.objects.get(id=sale_trade_id)
        
        strade.charge_confirm(charge_time=charge_time)
        
        saleservice = FlashSaleService(strade)
        saleservice.payTrade()
            
    except Exception,exc:
        raise confirmTradeChargeTask.retry(exc=exc)
            

@task(max_retry=3,default_retry_delay=60)
def notifyTradePayTask(notify):

    try:
        order_no = notify['order_no'].split('_')[0]
        charge   = notify['id']
        
        tcharge,state = TradeCharge.objects.get_or_create(order_no=order_no,charge=charge)
        
        if tcharge.paid == True:
            return
         
        update_fields = set(['paid','refunded','channel','amount','currency','transaction_no',
                         'amount_refunded','failure_code','failure_msg','time_paid','time_expire'])
    
        for k,v in notify.iteritems():
            if k not in update_fields:
                continue
            
            if k in ('time_paid','time_expire'):
                v = v and datetime.datetime.fromtimestamp(v)
            
            if k in ('failure_code','failure_msg'):
                v = v or ''
            
            hasattr(tcharge,k) and setattr(tcharge,k,v)
            
        tcharge.save()
        
        strade = SaleTrade.objects.get(tid=order_no)
        confirmTradeChargeTask(strade.id)
    
    except Exception,exc:
        raise notifyTradePayTask.retry(exc=exc)


from shopback.base import log_action, ADDITION, CHANGE 
from .options import getOrCreateSaleSeller

@task(max_retry=3,default_retry_delay=60)
def notifyTradeRefundTask(notify):
    
    try:
        refund_id = notify['id']
        
        seller = getOrCreateSaleSeller()
        srefund = SaleRefund.objects.get(refund_id=refund_id)
        
        log_action(seller.user.id,srefund,CHANGE,
                   u'%s(金额:%s)'%([u'退款失败',u'退款成功'][notify['succeed'] and 1 or 0],notify['amount']))
        
        if not notify['succeed']:
            logger.error('refund error:%s'%notify)
            return 
        
        srefund.refund_Confirm()
        
        strade = SaleTrade.objects.get(id=srefund.trade_id)
        if strade.is_Deposite_Order():
            return
        
        saleservice = FlashSaleService(strade)
        saleservice.payTrade()
    
    except Exception,exc:
        raise notifyTradeRefundTask.retry(exc=exc)
        

@task(max_retries=3,default_retry_delay=30)
def pushTradeRefundTask(refund_id):
    #退款申请
    try:
        sale_refund = SaleRefund.objects.get(id=refund_id)
        trade_id    = sale_refund.trade_id
        
        strade = SaleTrade.objects.get(id=trade_id)
        
        saleservice = FlashSaleService(strade)
        saleservice.payTrade()

        from shopback.refunds.models import Refund
        
        seller = getOrCreateSaleSeller()
        sorder = SaleOrder.objects.get(id=sale_refund.order_id)
        refund,state  = Refund.objects.get_or_create(tid=strade.tid,
                                                     oid=sorder.oid)
        
        refund.user = seller
        refund.title = sorder.title
        refund.payment = sale_refund.payment
        refund.buyer_nick = strade.buyer_nick or strade.receiver_name
        refund.mobile     = strade.receiver_mobile
        
        if sale_refund.has_good_return:
            refund.status = Refund.REFUND_WAIT_RETURN_GOODS
            refund.has_good_return = sale_refund.has_good_return
        else:
            refund.status = Refund.REFUND_WAIT_SELLER_AGREE
        
        refund.save()
        
    except Exception,exc:
        raise pushTradeRefundTask.retry(exc=exc)
        
            
@task
def push_SaleTrade_To_MergeTrade():
    """ 更新特卖订单到订单列表 """
    
    saletrades = SaleTrade.objects.filter(status=SaleTrade.WAIT_SELLER_SEND_GOODS)
    for strade in saletrades:
        mtrades = MergeTrade.objects.filter(tid=strade.tid,type=MergeTrade.SALE_TYPE)
        if mtrades.count() > 0 and mtrades[0].modified >= strade.modified:
            continue
        saleservice = FlashSaleService(strade)
        saleservice.payTrade()
        
import pingpp
from flashsale.pay.models import Envelop

@task
def task_Pull_Red_Envelope(pre_day=7):
    """更新红包 
    {
      "status": "SENDING", 
      "body": "\u4e00\u4efd\u8015\u8018\uff0c\u4e00\u4efd\u6536\u83b7\uff0c\u8c22\u8c22\u4f60\u7684\u52aa\u529b\uff01", 
      "object": "red_envelope", 
      "description": "\u5c0f\u9e7f\u5988\u5988\u7f16\u53f7:2540,\u63d0\u73b0\u524d:12160", 
      "order_no": "4348", 
      "extra": {
        "nick_name": "\u4e0a\u6d77\u5df1\u7f8e\u7f51\u7edc\u79d1\u6280", 
        "send_name": "\u5c0f\u9e7f\u7f8e\u7f8e"
      }, 
      "app": "app_LOOajDn9u9WDjfHa", 
      "livemode": true, 
      "paid": true, 
      "created": 1434975877, 
      "transaction_no": "100000000020150622316876646289", 
      "currency": "cny", 
      "amount": 5000, 
      "received": null, 
      "recipient": "our5huB4NHz2D7XTkdWTcurQXsYc", 
      "id": "red_9ujLmDSqPG8Ov5ab1C9WXLuH", 
      "channel": "wx_pub", 
      "subject": "\u94b1\u5305\u63d0\u73b0"
    }
    """
    today = datetime.datetime.now()
    pre_date = today - datetime.timedelta(days=pre_day)
    
    pingpp.api_key = settings.PINGPP_APPKEY
    
    page_size = 100
    has_next = True
    starting_after = None
    while has_next:
        if starting_after:
            resp = pingpp.RedEnvelope.all(limit=page_size,
                                          created={'gte':pre_date,'lte':today},
                                          starting_after=starting_after)  
        else:
            resp = pingpp.RedEnvelope.all(limit=page_size,
                                          created={'gte':pre_date,'lte':today})  
        
        for e in resp['data']:
            envelop = Envelop.objects.get(id=e['order_no'])
            envelop.handle_envelop(e)
        else:
            starting_after = e['id']
        
        has_next = resp['has_more']
        if not has_next:
            break
            

from models_coupon import CouponPool
from django.db import transaction


@task
@transaction.commit_on_success
def task_Update_CouponPoll_Status():
    today = datetime.datetime.today()
    # 定时更新优惠券的状态:超过截至时间的优惠券 将其状态修改为过期无效状态
    # 找到截至时间 是昨天的 优惠券
    deadline_time = datetime.datetime(today.year, today.month, today.day, 0, 0, 0) - datetime.timedelta(days=1)
    # 未发放的 已经发放的 可以使用的  （截至时间是昨天的）
    cous = CouponPool.objects.filter(deadline=deadline_time,
                                     coupon_status__in=(CouponPool.RELEASE, CouponPool.UNRELEASE, CouponPool.PULLED))
    for cou in cous:
        cou.coupon_status = CouponPool.PAST  # 修改为无效的优惠券
        cou.save()
