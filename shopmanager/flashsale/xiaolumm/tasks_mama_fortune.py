# -*- encoding:utf-8 -*-

from django.db.models import F, Sum
from django.db import IntegrityError
from celery.task import task

import logging

logger = logging.getLogger('celery.handler')

from flashsale.xiaolumm.models_fortune import MamaFortune, ActiveValue, OrderCarry, ReferalRelationship, CarryRecord, \
    GroupRelationship, MAMA_FORTUNE_HISTORY_LAST_DAY
from flashsale.xiaolumm.models import CashOut
from flashsale.xiaolumm.models_fans import XlmmFans

import sys, datetime, time


def get_cur_info():
    """Return the frame object for the caller's stack frame."""
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    # return (f.f_code.co_name, f.f_lineno)
    return f.f_code.co_name


def create_mamafortune_with_integrity(mama_id, **kwargs):
    # try:
    # fortune = MamaFortune(mama_id=mama_id, **kwargs)
    fortune = MamaFortune(mama_id=mama_id)
    for k, v in kwargs.iteritems():
        if hasattr(fortune, k):
            setattr(fortune, k, v)
    fortune.save()
    # except IntegrityError as e:
    # logger.warn("IntegrityError - mama_id: %s, params: %s" % (mama_id, kwargs))
    # The following will very likely cause deadlock, since another
    # thread is creating this record. we decide to just fail it.
    # MamaFortune.objects.filter(mama_id=mama_id).update(**kwargs)


@task(max_retries=3, default_retry_delay=6)
def task_xiaolumama_update_mamafortune(mama_id, cash):
    logger.warn("%s - mama_id: %s, params: %s" % (get_cur_info(), mama_id, cash))
    fortunes = MamaFortune.objects.filter(mama_id=mama_id)
    if fortunes.count() > 0:
        fortunes.update(history_confirmed=cash)
        # fortune = fortunes[0]
        # fortune.history_confirmed = cash
        # fortune.save()
    else:
        try:
            create_mamafortune_with_integrity(mama_id, history_confirmed=cash)
        except IntegrityError as exc:
            logger.warn("IntegrityError - MamaFortune | mama_id: %s, cash: %s" % (mama_id, cash))
            raise task_xiaolumama_update_mamafortune.retry(exc=exc)


CASHOUT_HISTORY_LAST_DAY_TIME = datetime.datetime(2016, 3, 30, 23, 59, 59)


@task(max_retries=3, default_retry_delay=6)
def task_cashout_update_mamafortune(mama_id):
    pending_record = CashOut.objects.filter(xlmm=mama_id,status=CashOut.PENDING).first()
    appr_comp_record = CashOut.objects.filter(xlmm=mama_id,status__in=(CashOut.APPROVED, CashOut.COMPLETED),
                                              approve_time__gt=CASHOUT_HISTORY_LAST_DAY_TIME).first()
    pstr,astr = None,None
    if pending_record:
        pstr = "%|%s" % (pending_record.id, pending_record.value)
    if appr_comp_record:
        astr = "%|%s" % (appr_comp_record.id, appr_comp_record.value)
    logger.warn("%s - mama_id: %s, pending: %s, appr_comp: %s" % (mama_id, pstr, astr)
                                              
    pending_res = CashOut.objects.filter(xlmm=mama_id,status=CashOut.PENDING).aggregate(total=Sum('value'))
    pending_cash = pending_res['total'] or 0

    cashout_res = CashOut.objects.filter(xlmm=mama_id,
                                         status__in=(CashOut.APPROVED, CashOut.COMPLETED),
                                         approve_time__gt=CASHOUT_HISTORY_LAST_DAY_TIME)\
        .aggregate(total=Sum('value'))

    effect_cashout = cashout_res['total'] or 0

    effect_cashout += pending_cash
    
    logger.warn("%s - mama_id: %s, effect_cashout: %s" % (get_cur_info(), mama_id, effect_cashout))
    fortunes = MamaFortune.objects.filter(mama_id=mama_id)
    if fortunes.count() > 0:
        fortune = fortunes[0]
        if fortune.carry_cashout != effect_cashout:
            fortune.carry_cashout = effect_cashout
            fortune.save(update_fields=['carry_cashout'])
    else:
        try:
            create_mamafortune_with_integrity(mama_id, carry_cashout=effect_cashout)
        except IntegrityError as exc:
            logger.warn("IntegrityError - MamaFortune cashout | mama_id: %s" % (mama_id))
            raise task_cashout_update_mamafortune.retry(exc=exc)


@task(max_retries=3, default_retry_delay=6)
def task_carryrecord_update_mamafortune(mama_id):
    print "%s, mama_id: %s" % (get_cur_info(), mama_id)

    carrys = CarryRecord.objects.filter(mama_id=mama_id, date_field__gt=MAMA_FORTUNE_HISTORY_LAST_DAY).values(
        'status').annotate(carry=Sum('carry_num'))
    carry_pending, carry_confirmed, carry_cashout = 0, 0, 0
    for entry in carrys:
        if entry["status"] == 1:  # pending
            carry_pending = entry["carry"]
        elif entry["status"] == 2:  # confirmed
            carry_confirmed = entry["carry"]

    fortunes = MamaFortune.objects.filter(mama_id=mama_id)
    if fortunes.count() > 0:
        fortune = fortunes[0]
        if fortune.carry_pending != carry_pending or fortune.carry_confirmed != carry_confirmed:
            fortunes.update(carry_pending=carry_pending, carry_confirmed=carry_confirmed)
            # fortune.carry_pending   = carry_pending
            # fortune.carry_confirmed = carry_confirmed
            # fortune.save()
    else:
        try:
            create_mamafortune_with_integrity(mama_id, carry_pending=carry_pending, carry_confirmed=carry_confirmed)
        except IntegrityError as exc:
            logger.warn("IntegrityError - MamaFortune carryrecord | mama_id: %s" % (mama_id))
            raise task_carryrecord_update_mamafortune.retry(exc=exc)


@task(max_retries=3, default_retry_delay=6)
def task_activevalue_update_mamafortune(mama_id):
    """
    更新妈妈activevalue
    """
    print "%s, mama_id: %s" % (get_cur_info(), mama_id)

    today = datetime.datetime.now().date()
    effect_day = today - datetime.timedelta(30)

    values = ActiveValue.objects.filter(mama_id=mama_id, date_field__gt=effect_day, status=2).values(
        'mama_id').annotate(value=Sum('value_num'))
    if values.count() <= 0:
        return

    value_num = values[0]["value"]

    mama_fortunes = MamaFortune.objects.filter(mama_id=mama_id)
    if mama_fortunes.count() > 0:
        mama_fortunes.update(active_value_num=value_num)
    else:
        try:
            create_mamafortune_with_integrity(mama_id, active_value_num=value_num)
        except IntegrityError as exc:
            logger.warn("IntegrityError - MamaFortune activevalue | mama_id: %s" % (mama_id))
            raise task_activevalue_update_mamafortune.retry(exc=exc)


@task(max_retries=3, default_retry_delay=6)
def task_update_mamafortune_invite_num(mama_id):
    print "%s, mama_id: %s" % (get_cur_info(), mama_id)

    records = ReferalRelationship.objects.filter(referal_from_mama_id=mama_id)
    invite_num = records.count()

    mamas = MamaFortune.objects.filter(mama_id=mama_id)
    if mamas.count() > 0:
        mama = mamas[0]
        if mama.invite_num != invite_num:
            mamas.update(invite_num=invite_num)
            # mama.invite_num=invite_num
            # mama.save()
    else:
        try:
            create_mamafortune_with_integrity(mama_id, invite_num=invite_num)
        except IntegrityError as exc:
            logger.warn("IntegrityError - MamaFortune invitenum | mama_id: %s" % (mama_id))
            raise task_update_mamafortune_invite_num.retry(exc=exc)


@task(max_retries=3, default_retry_delay=6)
def task_update_mamafortune_mama_level(mama_id):
    print "%s, mama_id: %s" % (get_cur_info(), mama_id)

    records = ReferalRelationship.objects.filter(referal_from_mama_id=mama_id)
    invite_num = records.count()

    groups = GroupRelationship.objects.filter(leader_mama_id=mama_id)
    group_num = groups.count()

    total = invite_num + group_num

    level = 0
    if invite_num >= 15 or total >= 50:
        level = 1
    if total >= 200:
        level = 2
    if total >= 500:
        level = 3
    if total >= 1000:
        level = 4

    mamas = MamaFortune.objects.filter(mama_id=mama_id)
    if mamas.count() > 0:
        mama = mamas[0]
        if mama.mama_level != level:
            mamas.update(mama_level=level)
            # mama.mama_level = level
            # mama.save()
    else:
        try:
            create_mamafortune_with_integrity(mama_id, mama_level=level)
        except IntegrityError as exc:
            logger.warn("IntegrityError - MamaFortune mamalevel | mama_id: %s" % (mama_id))
            raise task_update_mamafortune_mama_level.retry(exc=exc)


@task(max_retries=3, default_retry_delay=6)
def task_update_mamafortune_fans_num(mama_id):
    print "%s, mama_id: %s" % (get_cur_info(), mama_id)

    fans = XlmmFans.objects.filter(xlmm=mama_id)
    fans_num = fans.count()

    mamas = MamaFortune.objects.filter(mama_id=mama_id)
    if mamas.count() > 0:
        mamas.update(fans_num=fans_num)
    else:
        try:
            create_mamafortune_with_integrity(mama_id, fans_num=fans_num)
        except IntegrityError as exc:
            logger.warn("IntegrityError - MamaFortune fansnum | mama_id: %s" % (mama_id))
            raise task_update_mamafortune_fans_num.retry(exc=exc)


@task(max_retries=3, default_retry_delay=6)
def task_update_mamafortune_order_num(mama_id):
    print "%s, mama_id: %s" % (get_cur_info(), mama_id)
    records = OrderCarry.objects.filter(mama_id=mama_id).exclude(status=3).values('contributor_id')
    order_num = records.count()

    mamas = MamaFortune.objects.filter(mama_id=mama_id)
    if mamas.count() > 0:
        mamas.update(order_num=order_num)
    else:
        try:
            create_mamafortune_with_integrity(mama_id, order_num=order_num)
        except IntegrityError as exc:
            logger.warn("IntegrityError - MamaFortune ordernum | mama_id: %s" % (mama_id))
            raise task_update_mamafortune_order_num.retry(exc=exc)
