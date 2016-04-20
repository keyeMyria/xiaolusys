# coding: utf-8
# __author__ = 'linjie'
import datetime
import re

from django.db.models import Sum
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from rest_framework import permissions, viewsets
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response

from flashsale.xiaolumm.models import CarryLog

from .models import DailyStat, PopularizeCost


# 推广成本分类统计，包含（订单返利，代理补贴，点击补贴，…）
# 可以集成到 [flashsale.daystat] app里面


def get_month_from_date(date_time):
    day_from = datetime.date(date_time.year, date_time.month, 1)  # 这个月的开始时间
    if date_time.month == 12:
        day_to = datetime.date(date_time.year, date_time.month, 31)
    else:
        day_to = datetime.date(date_time.year, date_time.month + 1,
                               1) - datetime.timedelta(1)  # 这个月的第一天减去1天
    date_from = datetime.datetime(day_from.year, day_from.month, day_from.day,
                                  0, 0, 0)  # 上一周的开始时间
    date_to = datetime.datetime(day_to.year, day_to.month, day_to.day, 23, 59,
                                59)  # 上一周的结束时间
    return date_from, date_to


def popularize_Cost(request):
    content = request.REQUEST
    daystr = content.get("month", None)
    if daystr:
        year, month, day = daystr.split('-')
        target_date = datetime.datetime(int(year), int(month), int(day))
        date_from, date_to = get_month_from_date(target_date)
    else:
        target_date = datetime.datetime.now()
        date_from, date_to = get_month_from_date(target_date)
    prev_month = datetime.date(date_from.year, date_from.month,
                               date_from.day) - datetime.timedelta(days=1)
    next_month = datetime.date(date_to.year, date_to.month,
                               date_to.day) + datetime.timedelta(days=1)

    date_from = datetime.date(date_from.year, date_from.month, date_from.day)
    date_to = datetime.date(date_to.year, date_to.month, date_to.day)
    popularizes = PopularizeCost.objects.filter(date__gte=date_from,
                                                date__lte=date_to)

    date_dic = {"prev_month": prev_month, "next_month": next_month}
    return render_to_response("popularize/popularize_cost.html",
                              {"date_dic": date_dic,
                               'popularizes': popularizes},
                              context_instance=RequestContext(request))


class DailyStatsViewSet(viewsets.GenericViewSet):
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    template_name = 'xiaolumm/daily_stats.html'

    def list(self, request, *args, **kwargs):
        from flashsale.dinghuo.models import OrderList
        from flashsale.pay.models_refund import SaleRefund
        from shopback.trades.models import MergeOrder
        from shopback import paramconfig as pcfg

        if not re.search(r'application/json', request.META['HTTP_ACCEPT']):
            return Response()
        type_ = int(request.GET.get('type') or 0)
        if not type_:
            return Response({'error': '类型错误'})

        data = None
        now = datetime.datetime.now()
        threshold = now - datetime.timedelta(days=3)
        threshold2 = now - datetime.timedelta(days=5)
        if type_ == 1:
            q = MergeOrder.objects.filter(
                merge_trade__type__in=[pcfg.SALE_TYPE, pcfg.DIRECT_TYPE,
                                       pcfg.REISSUE_TYPE, pcfg.EXCHANGE_TYPE],
                merge_trade__sys_status__in=
                [pcfg.WAIT_AUDIT_STATUS, pcfg.WAIT_PREPARE_SEND_STATUS,
                 pcfg.WAIT_CHECK_BARCODE_STATUS, pcfg.WAIT_SCAN_WEIGHT_STATUS,
                 pcfg.REGULAR_REMAIN_STATUS],
                sys_status=pcfg.IN_EFFECT)

            n_total = q.only('id').count()
            n_delay = q.filter(pay_time__lte=threshold).only('id').count()
            n_s_delay = q.filter(pay_time__lte=threshold2).only('id').count()
            data = {'n_total': n_total, 'n_delay': n_delay, 'n_s_delay': n_s_delay}
        elif type_ == 2:
            q = SaleRefund.objects.filter(
                status__in=[SaleRefund.REFUND_WAIT_SELLER_AGREE, SaleRefund.REFUND_WAIT_RETURN_GOODS,
                            SaleRefund.REFUND_CONFIRM_GOODS, SaleRefund.REFUND_APPROVE])
            n_total = q.only('id').count()
            n_delay = q.filter(created__lte=threshold).only('id').count()
            n_s_delay = q.filter(created__lte=threshold2).only('id').count()
            data = {'n_total': n_total, 'n_delay': n_delay, 'n_s_delay': n_s_delay}
        elif type_ == 3:
            q = SaleRefund.objects.filter(status=SaleRefund.REFUND_APPROVE)
            n_total = q.only('id').count()
            n_delay = q.filter(created__lte=threshold).only('id').count()
            n_s_delay = q.filter(created__lte=threshold2).only('id').count()
            data = {'n_total': n_total, 'n_delay': n_delay, 'n_s_delay': n_s_delay}
        elif type_ == 4:
            q = OrderList.objects.exclude(status__in=[OrderList.COMPLETED, OrderList.ZUOFEI, OrderList.CLOSED])
            n_total = q.only('id').count()
            n_delay = q.filter(created__lte=threshold.date()).only('id').count()
            n_s_delay = q.filter(created__lte=threshold2.date()).only('id').count()
            data = {'n_total': n_total, 'n_delay': n_delay, 'n_s_delay': n_s_delay}
        if data:
            return Response(data)
        return Response({'error': '参数错误'})
