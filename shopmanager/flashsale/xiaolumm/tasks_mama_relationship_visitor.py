# -*- encoding:utf-8 -*-

from django.db.models import F
from django.db import IntegrityError
from celery.task import task
from flashsale.xiaolumm import util_description

import logging

logger = logging.getLogger('celery.handler')

from flashsale.xiaolumm.models_fortune import ReferalRelationship, GroupRelationship, UniqueVisitor
from flashsale.pay.models_user import Customer
from flashsale.xiaolumm.models import XiaoluMama

import sys


def get_cur_info():
    """Return the frame object for the caller's stack frame."""
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    # return (f.f_code.co_name, f.f_lineno)
    return f.f_code.co_name


@task()
def task_update_referal_relationship(sale_order):
    sale_trade = sale_order.sale_trade
    customer_id = sale_trade.buyer_id
    customer = Customer.objects.get(pk=customer_id)

    mamas = XiaoluMama.objects.filter(openid=customer.unionid)
    if mamas.count() <= 0:
        return

    # mama status is taken care of by some other logic, so we ignore.
    # mamas.update(status=XiaoluMama.EFFECT, progress=XiaoluMama.PAY, charge_status=XiaoluMama.CHARGED)
    to_mama_id = mamas[0].id

    extra = sale_trade.extras_info
    mm_linkid = 0
    if 'mm_linkid' in extra:
        mm_linkid = int(extra['mm_linkid'] or '0')

    if mm_linkid <= 0:
        return

    logger.warn("%s: mm_linkid=%s, to_mama_id=%s" % (get_cur_info(), mm_linkid, to_mama_id))

    records = ReferalRelationship.objects.filter(referal_to_mama_id=to_mama_id)
    if records.count() <= 0:
        record = ReferalRelationship(referal_from_mama_id=mm_linkid,
                                     referal_to_mama_id=to_mama_id,
                                     referal_to_mama_nick=customer.nick,
                                     referal_to_mama_img=customer.thumbnail)
        record.save()


@task()
def task_update_group_relationship(leader_mama_id, referal_relationship):
    print "%s, mama_id: %s" % (get_cur_info(), referal_relationship.referal_from_mama_id)

    records = GroupRelationship.objects.filter(member_mama_id=referal_relationship.referal_to_mama_id)
    if records.count() <= 0:
        record = GroupRelationship(leader_mama_id=leader_mama_id,
                                   referal_from_mama_id=referal_relationship.referal_from_mama_id,
                                   member_mama_id=referal_relationship.referal_to_mama_id,
                                   member_mama_nick=referal_relationship.referal_to_mama_nick,
                                   member_mama_img=referal_relationship.referal_to_mama_img)

        record.save()


from flashsale.xiaolumm.util_unikey import gen_uniquevisitor_unikey
from shopapp.weixin.options import get_unionid_by_openid


@task()
def task_update_unique_visitor(mama_id, openid, appkey, click_time):
    print "%s, mama_id: %s" % (get_cur_info(), mama_id)

    if XiaoluMama.objects.filter(pk=mama_id).count() <= 0:
        return

    nick, img = '', ''
    unionid = get_unionid_by_openid(openid, appkey)
    if unionid:
        customers = Customer.objects.filter(unionid=unionid)
        if customers.count() > 0:
            nick, img = customers[0].nick, customers[0].thumbnail
    else:
        # if no unionid exists, then use openid
        unionid = openid

    date_field = click_time.date()
    uni_key = gen_uniquevisitor_unikey(openid, date_field)

    try:
        visitor = UniqueVisitor(mama_id=mama_id, visitor_unionid=unionid, visitor_nick=nick,
                                visitor_img=img, uni_key=uni_key, date_field=date_field)
        visitor.save()
    except IntegrityError:
        logger.warn("IntegrityError - UniqueVisitor | mama_id: %s, uni_key: %s" % (mama_id, uni_key))
        pass
        # visitor already visited a mama's link, ignoring.


from flashsale.promotion.models_freesample import AppDownloadRecord
from flashsale.xiaolumm.models_fans import XlmmFans
from flashsale.xiaolumm.models import XiaoluMama


@task()
def task_login_update_fans(user):
    """
    All fans logic/relationship starts from here. Any other fans logic should be canceled.
    
    If AppDownloadRecord has multiple record for the same openid, we use the latest one.
    1) Only XiaoluMama can have fans;
    2) If I am a XiaoluMama, I should not be a fan of any other XiaoluMama;
    3) I should not be a fan of myself.
    """

    customers = Customer.objects.filter(user=user)
    if not customers.exists():
        return

    customer = customers[0]
    self_mama = customer.getXiaolumm()
    if self_mama:
        # XiaoluMama can't be a fan of any others.
        return
    
    unionid = customer.unionid
    mobile = customer.mobile

    records = None
    if unionid:
        records = AppDownloadRecord.objects.filter(unionid=unionid, status=AppDownloadRecord.UNUSE).order_by('-created')
    if records.count() <= 0 and mobile:
        records = AppDownloadRecord.objects.filter(mobile=mobile, status=AppDownloadRecord.UNUSE).order_by('-created')
    if not records or records.count() <= 0:
            return

    record = records[0]
    from_customer = record.from_customer
    referal_customer_id = from_customer

    customer1 = Customer.objects.get(id=from_customer)
    from_mama = customer1.getXiaolumm()

    mama_id, mama_customer_id = None, None
    if from_mama:
        mama_id = from_mama.id
        mama_customer_id = from_customer
    else:
        # if my parent is not xiaolumama, then find out indirect xiaolumama
        fan_records = XlmmFans.objects.filter(fans_cusid=from_customer)
        if fan_records.count() <= 0:
            return
        fan_record = fan_records[0]
        mama_id = fan_record.xlmm
        mama_customer_id = fan_record.xlmm_cusid

    fans = XlmmFans.objects.filter(fans_cusid=customer.id)
    if fans.count() > 0:
        return

    if mama_customer_id == customer.id:
        # self canot be self's fan
        return

    logger.warn("task_login_update_fans|mama_id:%s,mama_customer_id:%s,referal_customer_id:%s,fan_customer_id:%s, fan_nick:%s" % (mama_id, mama_customer_id, referal_customer_id, customer.id, customer.nick))
    fan = XlmmFans(xlmm=mama_id, xlmm_cusid=mama_customer_id, refreal_cusid=referal_customer_id, fans_cusid=customer.id,
                   fans_nick=customer.nick, fans_thumbnail=customer.thumbnail)
    fan.save()

    records.update(status=AppDownloadRecord.USED)
 
