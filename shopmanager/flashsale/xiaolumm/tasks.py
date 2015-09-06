#-*- encoding:utf8 -*-
import time
import datetime
from django.db.models import F,Sum,Q
from django.conf import settings
from celery.task import task

from flashsale.clickrebeta.models import StatisticsShopping
from flashsale.xiaolumm.models import Clicks,XiaoluMama,CarryLog, OrderRedPacket
from shopapp.weixin.models_base import WeixinUnionID as Base_WeixinUniID
from shopapp.weixin.models import WeixinUnionID,WXOrder

import logging
logger = logging.getLogger('celery.handler')

__author__ = 'meixqhi'

CLICK_REBETA_DAYS = 11
ORDER_REBETA_DAYS = 10
AGENCY_SUBSIDY_DAYS = 11
AGENCY_RECRUIT_DAYS = 3

@task()
def task_Create_Click_Record(xlmmid,openid,unionid,click_time):
    """
    异步保存妈妈分享点击记录
    xlmm_id:小鹿妈妈id,
    openid:妈妈微信openid,
    click_time:点击时间
    """
    xlmmid = int(xlmmid)
    
    today = datetime.datetime.now()
    tf = datetime.datetime(today.year,today.month,today.day,0,0,0)
    tt = datetime.datetime(today.year,today.month,today.day,23,59,59)
    
    isvalid = False
    clicks = Clicks.objects.filter(openid=openid,click_time__range=(tf,tt))
    click_linkids = set([l.get('linkid') for l in clicks.values('linkid').distinct()])
    click_count   = len(click_linkids)
    xlmms = XiaoluMama.objects.filter(id=xlmmid)
    
    if click_count < Clicks.CLICK_DAY_LIMIT and xlmms.count() > 0 and xlmmid not in click_linkids:
        isvalid = True
        
    Clicks.objects.create(linkid=xlmmid,openid=openid,isvalid=isvalid,click_time=click_time)
    
    WeixinUnionID.objects.get_or_create(openid=openid,app_key=settings.WEIXIN_APPID,unionid=unionid)
    

@task()
def task_Push_Pending_Carry_Cash(xlmm_id=None):
    """
    将待确认金额重新计算并加入妈妈现金账户
    xlmm_id:小鹿妈妈id
    """
    #结算订单提成
    task_Push_Pending_OrderRebeta_Cash(day_ago=ORDER_REBETA_DAYS, xlmm_id=xlmm_id)
    #结算点击补贴
    task_Push_Pending_ClickRebeta_Cash(day_ago=CLICK_REBETA_DAYS, xlmm_id=xlmm_id)
    #结算千元提成
    task_Push_Pending_ThousRebeta_Cash(day_ago=ORDER_REBETA_DAYS, xlmm_id=xlmm_id)
    
    recruit_date = datetime.date.today() - datetime.timedelta(days=AGENCY_RECRUIT_DAYS)
    
    c_logs = CarryLog.objects.filter(log_type__in=(#CarryLog.CLICK_REBETA,
                                                   #CarryLog.THOUSAND_REBETA,
                                                   CarryLog.MAMA_RECRUIT,
                                                   ),
                                     carry_date__lt=recruit_date,
                                     carry_type=CarryLog.CARRY_IN,
                                     status=CarryLog.PENDING)
    
    if xlmm_id:
        xlmm  = XiaoluMama.objects.get(id=xlmm_id)
        c_logs = c_logs.filter(xlmm=xlmm.id)
        
    for cl in c_logs:
        
        xlmms = XiaoluMama.objects.filter(id=cl.xlmm)
        if xlmms.count() == 0:
            continue
        
        xlmm = xlmms[0]
        #是否考试通过
        if not xlmm.exam_Passed():
            continue
        #重新计算pre_date之前订单金额，取消退款订单提成
        
        #将carrylog里的金额更新到最新，然后将金额写入mm的钱包帐户
        xlmm.push_carrylog_to_cash(cl)
        
RED_PACK_START_TIME = datetime.datetime(2015, 7, 6, 0, 0)       # 订单红包开放时间

def init_Data_Red_Packet():
    # 判断 xlmm 是否有过 首单 或者 十单  如果是的将 OrderRedPacket 状态修改过来
    xlmms = XiaoluMama.objects.filter(charge_status=XiaoluMama.CHARGED, agencylevel=2)
    
    for xlmm in xlmms:
        try:
            # 找订单
            shoppings = StatisticsShopping.objects.filter(linkid=xlmm.id, shoptime__lt=RED_PACK_START_TIME)
            if shoppings.count() >= 10:
                red_packet, state = OrderRedPacket.objects.get_or_create(xlmm=xlmm.id)
                red_packet.first_red = True  # 默认发放过首单红包
                red_packet.ten_order_red = True  # 默认发放过十单红包
                red_packet.save()
                xlmm.hasale = True
            elif shoppings.count() >= 1:
                red_packet, state = OrderRedPacket.objects.get_or_create(xlmm=xlmm.id)
                red_packet.first_red = True     # 默认发放过首单红包
                red_packet.save()
                xlmm.hasale = True
                
            xlmm.save()
        except Exception,exc:
            print 'exc:%s,%s'%(exc.message,xlmm.id)
            

from django.db import transaction
from shopback.trades.models import MergeTrade,MergeBuyerTrade

def shoptime_To_DateStr(shoptime):
    return shoptime.strftime("%Y-%m-%d")

def buyer_Num(xlmm, finish=False):
    if finish is False:
        shops = StatisticsShopping.objects.filter(linkid=xlmm).exclude(status=StatisticsShopping.REFUNDED)
    else:
        shops = StatisticsShopping.objects.filter(linkid=xlmm, status=StatisticsShopping.FINISHED)
    t_dict = {}
    for p in shops:
        shop_time = shoptime_To_DateStr(p.shoptime)
        if shop_time in t_dict:
            t_dict[shop_time].append(p.openid)
        else:
            t_dict[shop_time] = [p.openid]
    buyercount = 0
    for k, v in t_dict.items():
        buyercount += len(set(v))
    return buyercount


@transaction.commit_on_success
def order_Red_Packet_Pending_Carry(xlmm, target_date):
    
    today = datetime.date.today()
    if today < RED_PACK_START_TIME.date():
        return   # 开始时间之前 不执行订单红包
    # 2015-07-04 上午  要求修改为pending状态
    # 2015-07-04 要求 修改不使用红包（Envelop）， 使用CarryLog
   

    mama = XiaoluMama.objects.get(id=xlmm)
    if mama.agencylevel != 2:
        return
    red_packet, state = OrderRedPacket.objects.get_or_create(xlmm=xlmm)
    # 据要求2015-07-11 修改为 按照人数来发放红包
    buyercount = buyer_Num(xlmm, finish=False)
    if red_packet.first_red is False and mama.agencylevel == 2 and mama.charge_status == XiaoluMama.CHARGED:
    # 判断 xlmm 在 OrderRedPacket 中的首单状态  是False 则执行下面的语句
        if buyercount >= 1:
            # 写CarryLog记录，一条IN（生成红包）
            order_red_carry_log = CarryLog(xlmm=xlmm, value=880, buyer_nick=mama.weikefu,
                                           log_type=CarryLog.ORDER_RED_PAC,
                                           carry_type=CarryLog.CARRY_IN, status=CarryLog.PENDING,
                                           carry_date=today)
            order_red_carry_log.save()  # 保存
            red_packet.first_red = True  # 已经发放首单红包
            red_packet.save()   # 保存红包状态
    if red_packet.ten_order_red is False and mama.agencylevel == 2 and mama.charge_status == XiaoluMama.CHARGED:
    #  判断 xlmm 在 OrderRedPacket 中的十单状态 是False 则执行下面语句
        if buyercount >= 10:
            # 写CarryLog记录，一条IN（生成红包）
            order_red_carry_log = CarryLog(xlmm=xlmm, value=1880, buyer_nick=mama.weikefu,
                                           log_type=CarryLog.ORDER_RED_PAC,
                                           carry_type=CarryLog.CARRY_IN, status=CarryLog.PENDING,
                                           carry_date=today)
            order_red_carry_log.save()  # 保存
            red_packet.first_red = True  # 已经发放首单红包
            red_packet.ten_order_red = True  # 已经发放10单红包
            red_packet.save()   # 保存红包状态

@transaction.commit_on_success
def order_Red_Packet(xlmm):
    mama = XiaoluMama.objects.get(id=xlmm)
    if mama.agencylevel == 2:
        # 寻找该妈妈以前的首单/十单红包记录
        red_pac_carry_logs = CarryLog.objects.filter(xlmm=xlmm, log_type=CarryLog.ORDER_RED_PAC, carry_type=CarryLog.CARRY_IN)
        buyercount = buyer_Num(xlmm, finish=True)
        if buyercount >= 10:
            for red_pac_carry_log in red_pac_carry_logs:
                if red_pac_carry_log.status == CarryLog.PENDING:    # 如果是PENDING则修改
                    mama.push_carrylog_to_cash(red_pac_carry_log)

        if buyercount >= 1 and buyercount < 10:
            for red_pac_carry_log in red_pac_carry_logs:
                if red_pac_carry_log.value == 880 and red_pac_carry_log.status == CarryLog.PENDING:
                    mama.push_carrylog_to_cash(red_pac_carry_log)


def update_Xlmm_Shopping_OrderStatus(order_list):
    """ 更新小鹿妈妈交易订单状态 """
    for order in order_list:
        trades = MergeTrade.objects.filter(tid=order.wxorderid,
                                        type__in=(MergeTrade.WX_TYPE,MergeTrade.SALE_TYPE))
        if trades.count() == 0:
            continue
        
        trade = trades[0]
        if trade.sys_status == MergeTrade.INVALID_STATUS or trade.status == MergeTrade.TRADE_CLOSED:
            order.status = StatisticsShopping.REFUNDED
        elif trade.sys_status == MergeTrade.FINISHED_STATUS:
            order.status = StatisticsShopping.FINISHED

        order.save()

@task()
def task_Update_Xlmm_Order_By_Day(xlmm,target_date):
    """
    更新每天妈妈订单状态及提成
    xlmm_id:小鹿妈妈id，
    target_date：计算日期
    """
    time_from = datetime.datetime(target_date.year, target_date.month, target_date.day)
    time_to = datetime.datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
    
    shoping_orders = StatisticsShopping.objects.filter(linkid=xlmm,shoptime__range=(time_from,time_to))
    #更新小鹿妈妈交易订单状态
    update_Xlmm_Shopping_OrderStatus(shoping_orders)
    
    try:
        order_Red_Packet(xlmm)
    except Exception,exc:
        logger.error(exc.message or 'Order Red Packet Error',exc_info=True)
        

@task()
def task_Push_Pending_ClickRebeta_Cash(day_ago=CLICK_REBETA_DAYS, xlmm_id=None):
    """
    计算待确认点击提成并计入妈妈现金帐号
    xlmm_id:小鹿妈妈id，
    day_ago：计算时间 = 当前时间 - 前几天
    """
    from flashsale.clickcount.tasks import calc_Xlmm_ClickRebeta
    pre_date = datetime.date.today() - datetime.timedelta(days=day_ago)
    c_logs = CarryLog.objects.filter(log_type=CarryLog.CLICK_REBETA, 
                                     carry_date__lte=pre_date,
                                     status=CarryLog.PENDING,
                                     carry_type=CarryLog.CARRY_IN)
    
    if xlmm_id:
        c_logs = c_logs.filter(xlmm=xlmm_id)
        
    for cl in c_logs:
        xlmms = XiaoluMama.objects.filter(id=cl.xlmm)
        if xlmms.count() == 0:
            continue
        
        xlmm = xlmms[0]
#         #是否考试通过
#         if not xlmm.exam_Passed():
#             continue
        
        #重新计算pre_date之前订单金额，取消退款订单提成
        carry_date = cl.carry_date
        task_Update_Xlmm_Order_By_Day(xlmm.id,carry_date)
        
        time_from = datetime.datetime(carry_date.year, carry_date.month, carry_date.day)
        time_to = datetime.datetime(carry_date.year, carry_date.month, carry_date.day, 23, 59, 59)
        
        click_rebeta = calc_Xlmm_ClickRebeta(xlmm,time_from,time_to)
        
        clog = CarryLog.objects.get(id=cl.id)
        if clog.status != CarryLog.PENDING:
            continue
        #将carrylog里的金额更新到最新，然后将金额写入mm的钱包帐户
        clog.value   = click_rebeta
        clog.save()        
        xlmm.push_carrylog_to_cash(clog)


@task()
def task_Push_Pending_OrderRebeta_Cash(day_ago=ORDER_REBETA_DAYS, xlmm_id=None):
    """
    计算待确认订单提成并计入妈妈现金帐号
    xlmm_id:小鹿妈妈id，
    day_ago：计算时间 = 当前时间 - 前几天
    """
    pre_date = datetime.date.today() - datetime.timedelta(days=day_ago)
    
    c_logs = CarryLog.objects.filter(log_type=CarryLog.ORDER_REBETA, 
                                     carry_date__lte=pre_date,
                                     status=CarryLog.PENDING,
                                     carry_type=CarryLog.CARRY_IN)

    if xlmm_id:
        c_logs = c_logs.filter(xlmm=xlmm_id)
    
    for cl in c_logs:
        
        xlmms = XiaoluMama.objects.filter(id=cl.xlmm)
        if xlmms.count() == 0:
            continue
        
        xlmm = xlmms[0]
        #是否考试通过
        if not xlmm.exam_Passed():
            continue
        
        #重新计算pre_date之前订单金额，取消退款订单提成
        carry_date = cl.carry_date
        task_Update_Xlmm_Order_By_Day(xlmm.id,carry_date)
        
        time_from = datetime.datetime(carry_date.year, carry_date.month, carry_date.day)
        time_to = datetime.datetime(carry_date.year, carry_date.month, carry_date.day, 23, 59, 59)
        shopings = StatisticsShopping.objects.filter(linkid=xlmm.id,
                                                 status__in=(StatisticsShopping.WAIT_SEND,StatisticsShopping.FINISHED),
                                                shoptime__range=(time_from,time_to))
        
        rebeta_fee = shopings.aggregate(total_rebeta=Sum('tichengcount')).get('total_rebeta') or 0
        
        #将carrylog里的金额更新到最新，然后将金额写入mm的钱包帐户
        
        clog = CarryLog.objects.get(id=cl.id)
        if clog.status != CarryLog.PENDING:
            continue
        
        clog.value     = rebeta_fee
        clog.save()
        
        xlmm.push_carrylog_to_cash(cl)
        
        
@task()
def task_Push_Pending_AgencyRebeta_Cash(day_ago=AGENCY_SUBSIDY_DAYS, xlmm_id=None):
    """
    计算代理贡献订单提成
    xlmm_id:小鹿妈妈id，
    day_ago：计算时间 = 当前时间 - 前几天
    """
    pre_date = datetime.date.today() - datetime.timedelta(days=day_ago)
    
    c_logs = CarryLog.objects.filter(log_type=CarryLog.AGENCY_SUBSIDY,
                                     carry_date__lte=pre_date,
                                     status=CarryLog.PENDING,
                                     carry_type=CarryLog.CARRY_IN)
    
    if xlmm_id:
        c_logs = c_logs.filter(xlmm=xlmm_id)
    
    for cl in c_logs:
        xlmms = XiaoluMama.objects.filter(id=cl.xlmm)
        if xlmms.count() == 0:
            continue
        
        xlmm = xlmms[0]
        #是否考试通过
        if not xlmm.exam_Passed():
            continue
        
        #重新计算pre_date之前订单金额，取消退款订单提成
        carry_date = cl.carry_date
        time_from = datetime.datetime(carry_date.year, carry_date.month, carry_date.day)
        time_to = datetime.datetime(carry_date.year, carry_date.month, carry_date.day, 23, 59, 59)
        shopings = StatisticsShopping.objects.filter(linkid=cl.order_num,
                                                 status__in=(StatisticsShopping.WAIT_SEND,StatisticsShopping.FINISHED),
                                                 shoptime__range=(time_from,time_to))
        
        calc_fee = shopings.aggregate(total_amount=Sum('rebetamount')).get('total_amount') or 0
        agency_rebeta_rate  = xlmm.get_Mama_Agency_Rebeta_Rate()
        agency_rebeta       = calc_fee * agency_rebeta_rate
        
        clog = CarryLog.objects.get(id=cl.id)
        if clog.status != CarryLog.PENDING or agency_rebeta > clog.value:
            continue
        #将carrylog里的金额更新到最新，然后将金额写入mm的钱包帐户
        
        clog.value  = agency_rebeta
        clog.save() 
        
        xlmm.push_carrylog_to_cash(clog)
        

from flashsale.clickrebeta.models import StatisticsShopping
### 代理提成表 的task任务  每个月 8号执行 计算 订单成交额超过1000人民币的提成
def calc_Mama_Thousand_Rebeta(xlmm,start,end):
    # 千元补贴
    shoppings = StatisticsShopping.objects.filter(
        linkid=xlmm.id, 
        shoptime__range=(start,end),
        status__in=(StatisticsShopping.WAIT_SEND,StatisticsShopping.FINISHED)
    )
    # 过去一个月的成交额
    sum_wxorderamount = shoppings.aggregate(total_order_amount=Sum('rebetamount')).get('total_order_amount') or 0
    
    return sum_wxorderamount


@task()
def task_ThousandRebeta(date_from,date_to):
    """
    计算千元提成
    date_from: 开始日期，
    date_to：结束日期
    """
    carry_no = date_from.strftime('%y%m%d')
    xlmms = XiaoluMama.objects.filter(charge_status=XiaoluMama.CHARGED) 
    for xlmm in xlmms:
        commission = calc_Mama_Thousand_Rebeta(xlmm,date_from,date_to)
        c_logs = CarryLog.objects.filter(xlmm=xlmm.id,order_num=carry_no,log_type=CarryLog.THOUSAND_REBETA)
        if c_logs.count() > 0 or commission >= xlmm.get_Mama_Thousand_Target_Amount() * 100: # 分单位
            # 写一条carry_log记录
            carry_log, state = CarryLog.objects.get_or_create(xlmm=xlmm.id,order_num=carry_no,
                                                              log_type=CarryLog.THOUSAND_REBETA)
            if not state and carry_log.status != CarryLog.PENDING:
                continue
            
            carry_log.buyer_nick = xlmm.mobile
            carry_log.carry_type = CarryLog.CARRY_IN
            carry_log.value      = commission * xlmm.get_Mama_Thousand_Rate()   # 上个月的千元提成
            carry_log.buyer_nick = xlmm.mobile
            carry_log.status     = CarryLog.PENDING
            carry_log.save()


def get_pre_month(year,month):
    
    if month == 1:
        return year - 1, 12
    return year,month - 1
    
import calendar

@task
def task_Calc_Month_ThousRebeta(pre_month=1):
    """
    按月计算千元代理提成
    pre_month:计算过去第几个月
    """
    today = datetime.datetime.now()
    year,month = today.year,today.month
    for m in range(pre_month):
        year,month = get_pre_month(year,month)
    
    month_range = calendar.monthrange(year,month)
    
    date_from = datetime.datetime(year,month,1,0,0,0)
    date_to   = datetime.datetime(year,month,month_range[1],23,59,59)
    
    task_ThousandRebeta(date_from,date_to)
    
    
@task()
def task_Push_Pending_ThousRebeta_Cash(day_ago=ORDER_REBETA_DAYS, xlmm_id=None):
    """
    计算待确认千元提成并计入妈妈现金帐号
    xlmm_id:小鹿妈妈id，
    day_ago：计算时间 = 当前时间 - 前几天
    """
    pre_date = datetime.date.today() - datetime.timedelta(days=day_ago)
    
    c_logs = CarryLog.objects.filter(log_type=CarryLog.THOUSAND_REBETA, 
                                     carry_date__lte=pre_date,
                                     status=CarryLog.PENDING,
                                     carry_type=CarryLog.CARRY_IN)
    
    if xlmm_id:
        c_logs = c_logs.filter(xlmm=xlmm_id)
    
    for cl in c_logs:
        xlmms = XiaoluMama.objects.filter(id=cl.xlmm)
        if xlmms.count() == 0:
            continue
        
        xlmm = xlmms[0]
        #是否考试通过
        if not xlmm.exam_Passed():
            continue
        
        #重新计算pre_date之前订单金额，取消退款订单提成
        carry_date = cl.carry_date
        pre_year,pre_month = get_pre_month(carry_date.year,carry_date.month)
        
        month_range = calendar.monthrange(pre_year,pre_month)
    
        date_from = datetime.datetime(pre_year,pre_month,1,0,0,0)
        date_to   = datetime.datetime(pre_year,pre_month,month_range[1],23,59,59)
        
        thousand_rebeta = calc_Mama_Thousand_Rebeta(xlmm,date_from,date_to)
        commission_fee  = thousand_rebeta * xlmm.get_Mama_Thousand_Rate()
        #将carrylog里的金额更新到最新，然后将金额写入mm的钱包帐户
        
        clog = CarryLog.objects.get(id=cl.id)
        if clog.status != CarryLog.PENDING or commission_fee > clog.value:
            continue
        
        clog.value     = commission_fee
        clog.save()
        
        xlmm.push_carrylog_to_cash(cl)

### 代理提成表 的task任务   计算 每个妈妈的代理提成，上交的给推荐人的提成


@task()
def task_AgencySubsidy_MamaContribu(target_date):      # 每天 写入记录
    """
    计算每日代理提成
    """
    time_from = datetime.datetime(target_date.year, target_date.month, target_date.day)  # 生成带时间的格式  开始时间
    time_to = datetime.datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)  # 停止时间
    
    xlmms = XiaoluMama.objects.normal_queryset.filter(charge_status=XiaoluMama.CHARGED) # 过滤出已经接管的类别是2的代理
    for xlmm in xlmms:
        sub_xlmms = XiaoluMama.objects.normal_queryset.filter(referal_from=xlmm.mobile,charge_status=XiaoluMama.CHARGED)  # 找到的本代理的子代理
        sum_wxorderamount = 0  # 昨天订单总额
        for sub_xlmm in sub_xlmms:
            # 扣除记录
            sub_shoppings = StatisticsShopping.objects.filter(linkid=sub_xlmm.id,
                                                              shoptime__range=(time_from,time_to),
                                                              status__in=(StatisticsShopping.WAIT_SEND,
                                                                          StatisticsShopping.FINISHED))
            # 过滤出子代理昨天的订单
            sum_wxorderamount = sub_shoppings.aggregate(total_order_amount=Sum('rebetamount')).get('total_order_amount') or 0
            
            commission = sum_wxorderamount * xlmm.get_Mama_Agency_Rebeta_Rate()
            if commission == 0:  # 如果订单总额是0则不做记录
                continue
            
            carry_log_f,state  = CarryLog.objects.get_or_create(xlmm=xlmm.id,order_num=sub_xlmm.id,
                                                          carry_date = target_date,
                                                          log_type=CarryLog.AGENCY_SUBSIDY)
            if not state and carry_log_f.status != CarryLog.PENDING:
                continue
#             carry_log_f.xlmm       = xlmm.id  # 锁定本代理
#             carry_log_f.order_num  = sub_xlmm.id      # 这里写的是子代理的ID
            carry_log_f.buyer_nick = xlmm.mobile
            carry_log_f.carry_type = CarryLog.CARRY_IN
            carry_log_f.value      = commission  # 上个月给本代理的分成
#             carry_log_f.carry_date = target_date
            carry_log_f.status     = CarryLog.PENDING
            carry_log_f.save()

@task
def task_Calc_Agency_Contribu(pre_day=1):
    
    pre_date = datetime.date.today() - datetime.timedelta(days=pre_day)
    
    task_AgencySubsidy_MamaContribu(pre_date)
    

@task
def task_Calc_Agency_Rebeta_Pending_And_Cash():
    
    #计算妈妈昨日代理贡献金额
    task_Calc_Agency_Contribu(pre_day=1)
    #计算妈妈昨日代理确认金额
    task_Push_Pending_AgencyRebeta_Cash(day_ago=AGENCY_SUBSIDY_DAYS)


from flashsale.xiaolumm.models import MamaDayStats
from flashsale.clickcount.models import ClickCount
from flashsale.clickrebeta.models import StatisticsShoppingByDay

def calc_mama_roi(xlmm,dfrom,dto):
    
    xlmm_id = xlmm.id

    xlmm_ccs =  ClickCount.objects.filter(date__range=(dfrom,dto),linkid=xlmm_id)
    valid_num = xlmm_ccs.aggregate(total_validnum=Sum('valid_num')).get('total_validnum') or 0
    
    xlmm_ssd  = StatisticsShoppingByDay.objects.filter(tongjidate__range=(dfrom,dto),linkid=xlmm_id)
    buyer_num = xlmm_ssd.aggregate(total_buyernum=Sum('buyercount')).get('total_buyernum') or 0
    payment   = xlmm_ssd.aggregate(total_amount=Sum('orderamountcount')).get('total_amount') or 0
    
    return valid_num, buyer_num, payment 

### 代理提成表 的task任务   计算 每个妈妈的代理提成，上交的给推荐人的提成
@task()
def task_Calc_Mama_Lasttwoweek_Stats(pre_day=0):      # 每天 写入记录
    """
    计算每日妈妈过去两周点击转化
    """
    
    target_date = datetime.date.today() - datetime.timedelta(days=pre_day)
    
    lweek_from  = target_date - datetime.timedelta(days=7)   # 生成带时间的格式  开始时间
    tweek_from  = target_date - datetime.timedelta(days=14)  # 停止时间

    xlmms = XiaoluMama.objects.filter(agencylevel=2) 
    for xlmm in xlmms:
        
        lweek_ds = calc_mama_roi(xlmm,lweek_from,target_date)
        tweek_ds = calc_mama_roi(xlmm,tweek_from,target_date)
        
        mm_stats, state = MamaDayStats.objects.get_or_create(
                                xlmm=xlmm.id,day_date=target_date)
        
        mm_stats.lweek_clicks = lweek_ds[0]
        mm_stats.lweek_buyers = lweek_ds[1]
        mm_stats.lweek_payment = lweek_ds[2]
        
        mm_stats.tweek_clicks = tweek_ds[0]
        mm_stats.tweek_buyers = tweek_ds[1]
        mm_stats.tweek_payment = tweek_ds[2]
        
        mm_stats.base_click_price = mm_stats.calc_click_price()
        mm_stats.save()
        

@task()
def task_Push_WXOrder_Finished(pre_days=10):
    """ 定时将待确认状态微信小店订单更新成已完成 """
    
    day_date = datetime.datetime.now() - datetime.timedelta(days=pre_days)
    
    SHIP_STATUS_MAP = {WXOrder.WX_CLOSE:StatisticsShopping.REFUNDED,
                       WXOrder.WX_FINISHED:StatisticsShopping.FINISHED}
    wxorders = WXOrder.objects.filter(order_status=WXOrder.WX_WAIT_CONFIRM)
    for wxorder in wxorders:
        wxorder_id = wxorder.order_id
        mtrades = MergeTrade.objects.filter(tid=wxorder_id,type=MergeTrade.WX_TYPE)
        if mtrades.count() == 0:
            continue
        
        mtrade = mtrades[0]
        if (mtrade.status == MergeTrade.TRADE_CLOSED or 
            mtrade.sys_status in (MergeTrade.INVALID_STATUS,MergeTrade.EMPTY_STATUS)):
            wxorder.order_status =  WXOrder.WX_CLOSE
            wxorder.save()
        
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
                
            morders = mtrade.normal_orders.filter(oid=wxorder_id)
            if (morders.count() == 0 or 
                morders[0].status in (MergeTrade.TRADE_CLOSED,
                                      MergeTrade.TRADE_REFUNDED,
                                      MergeTrade.TRADE_REFUNDING)):
                wxorder.order_status =  WXOrder.WX_CLOSE
                wxorder.save()
            else:
                wxorder.order_status =  WXOrder.WX_FINISHED
                wxorder.save()
        
        ship_trades = StatisticsShopping.objects.filter(wxorderid=wxorder_id)
        if ship_trades.count() > 0:
            ship_trade = ship_trades[0]
            ship_trade.status = SHIP_STATUS_MAP.get(wxorder.order_status,StatisticsShopping.WAIT_SEND)
            ship_trade.save()


@task
def task_Update_Sale_And_Weixin_Order_Status(pre_days=10):
    
    task_Push_WXOrder_Finished.s(pre_days=pre_days)()
    
    from flashsale.pay.tasks import task_Push_SaleTrade_Finished
    
    task_Push_SaleTrade_Finished.s(pre_days=pre_days)()


from .tasks_manager_summary import task_make_Manager_Summary_Cvs
# 引入任务文件