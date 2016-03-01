# coding:utf-8
__author__ = 'yann'

import datetime
import logging
from cStringIO import StringIO

from django.db.models import F
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from common.utils import CSVUnicodeWriter
from flashsale.dinghuo import log_action, CHANGE
from flashsale.dinghuo.models import OrderDetail, OrderList, orderdraft
import functions
from shopback.items.models import Product, ProductSku
from supplychain.supplier.models import SaleProduct

class ChangeDetailView(View):

    @staticmethod
    def get(request, order_detail_id):
        order_list = OrderList.objects.get(id=order_detail_id)
        order_details = OrderDetail.objects.filter(orderlist_id=order_detail_id)
        flag_of_status = False
        flag_of_question = False
        flag_of_sample = False
        order_list_list = []
        product_links = []
        for order in order_details:
            product = Product.objects.get(id=order.product_id)
            order_dict = model_to_dict(order)
            order_dict['pic_path'] = product.pic_path
            order_dict['supplier_outer_id'] = ProductSku.objects.get(
                id=order.chichu_id).outer_id
            if product.sale_product:
                try:
                    saleproduct = SaleProduct.objects.get(id=product.sale_product)
                    order_dict['product_link'] = saleproduct.product_link or ''
                except:
                    pass
            order_list_list.append(order_dict)
        def _sort(x):
            _M = {
                'XS': 1001,
                'S': 1002,
                'M': 1003,
                'L': 1004,
                'XL': 1005,
                'XXL': 1006,
                '3XL': 1007,
                '4XL': 1008,
                u'均码': 9999
            }
            chicun = x.get('product_chicun') or ''
            try:
                w = float(chicun)
            except:
                w = _M.get(chicun) or chicun
            return x.get('product_id') or 0, w
        order_list_list = sorted(order_list_list, key=_sort)

        product_link = product_links[0] if product_links else ''
        if order_list.status == "草稿":
            flag_of_status = True
        elif order_list.status == u'有问题' or order_list.status == u'5' or order_list.status == u'6':
            flag_of_question = True
        if order_list.status == u'7':
            flag_of_sample = True
        return render_to_response("dinghuo/changedetail.html",
                                  {"orderlist": order_list,
                                   "flagofstatus": flag_of_status,
                                   "flagofquestion": flag_of_question,
                                   "flag_of_sample": flag_of_sample,
                                   "orderdetails": order_list_list, 'product_link': product_link},
                                  context_instance=RequestContext(request))

    @staticmethod
    def post(request, order_detail_id):
        post = request.POST
        order_list = OrderList.objects.get(id=order_detail_id)
        status = post.get("status", "").strip()
        remarks = post.get("remarks", "").strip()
        if len(status) > 0 and len(remarks) > 0:
            if status == '已处理(需收款)':
                order_list.pay_status = '需收款'
            order_list.status = status
            order_list.note = order_list.note + "\n" + "-->" + datetime.datetime.now(
            ).strftime('%m月%d %H:%M') + request.user.username + ":" + remarks
            order_list.save()
            log_action(request.user.id, order_list, CHANGE, u'%s 订货单' %
                       (u'添加备注'))
        order_details = OrderDetail.objects.filter(orderlist_id=order_detail_id)
        order_list_list = []
        for order in order_details:
            order.non_arrival_quantity = order.buy_quantity - order.arrival_quantity - order.inferior_quantity
            order.save()
            order_dict = model_to_dict(order)
            order_dict['pic_path'] = Product.objects.get(
                id=order.product_id).pic_path
            order_list_list.append(order_dict)
        if order_list.status == "草稿":
            flag_of_status = True
        else:
            flag_of_status = False
        flag_of_sample = False
        if order_list.status == u'7':
            flag_of_sample = True
        #是否到货商品关联订单
        try:
            from shopback.items.tasks import releaseProductTradesTask
            distinct_pids = [
                p['product_id']
                for p in order_details.values('product_id').distinct()
            ]
            outer_ids = [p['outer_id']
                         for p in Product.objects.filter(
                             id__in=distinct_pids).values('outer_id')]
            releaseProductTradesTask.s(outer_ids)()
        except Exception, exc:
            logger = logging.getLogger('django.request')
            logger.error(exc.message, exc_info=True)

        return render_to_response("dinghuo/changedetail.html",
                                  {"orderlist": order_list,
                                   "flagofstatus": flag_of_status,
                                   "orderdetails": order_list_list,
                                   "flag_of_sample": flag_of_sample},
                                  context_instance=RequestContext(request))


class AutoNewOrder(View):

    @staticmethod
    def get(request, order_list_id):
        user = request.user
        functions.save_draft_from_detail_id(order_list_id, user)
        all_drafts = orderdraft.objects.all().filter(buyer_name=user)
        return render_to_response("dinghuo/shengchengorder.html",
                                  {"orderdraft": all_drafts},
                                  context_instance=RequestContext(request))


@csrf_exempt
def change_inferior_num(request):
    post = request.POST
    flag = post['flag']
    order_detail_id = post["order_detail_id"].strip()
    order_detail = OrderDetail.objects.get(id=order_detail_id)
    order_list = OrderList.objects.get(id=order_detail.orderlist_id)
    if flag == "0":
        if order_detail.inferior_quantity == 0:
            return HttpResponse("false")
        OrderDetail.objects.filter(id=order_detail_id).update(
            inferior_quantity=F('inferior_quantity') - 1)
        OrderDetail.objects.filter(id=order_detail_id).update(
            non_arrival_quantity=F('buy_quantity') - F('arrival_quantity') - F(
                'inferior_quantity'))
        OrderDetail.objects.filter(id=order_detail_id).update(
            arrival_quantity=F('arrival_quantity') + 1)
        Product.objects.filter(id=order_detail.product_id).update(
            collect_num=F('collect_num') + 1)
        ProductSku.objects.filter(id=order_detail.chichu_id).update(
            quantity=F('quantity') + 1)
        log_action(request.user.id, order_list, CHANGE, u'订货单{0}{1}{2}'.format(
            (u'次品减一件'), order_detail.product_name, order_detail.product_chicun))
        log_action(request.user.id, order_detail, CHANGE, u'%s' % (u'次品减一'))
        return HttpResponse("OK")
    elif flag == "1":
        OrderDetail.objects.filter(id=order_detail_id).update(
            inferior_quantity=F('inferior_quantity') + 1)
        OrderDetail.objects.filter(id=order_detail_id).update(
            non_arrival_quantity=F('buy_quantity') - F('arrival_quantity') - F(
                'inferior_quantity'))
        OrderDetail.objects.filter(id=order_detail_id).update(
            arrival_quantity=F('arrival_quantity') - 1)
        Product.objects.filter(id=order_detail.product_id).update(
            collect_num=F('collect_num') - 1)
        ProductSku.objects.filter(id=order_detail.chichu_id).update(
            quantity=F('quantity') - 1)
        log_action(request.user.id, order_list, CHANGE, u'订货单{0}{1}{2}'.format(
            (u'次品加一件'), order_detail.product_name, order_detail.product_chicun))
        log_action(request.user.id, order_detail, CHANGE, u'%s' % (u'次品加一'))
        return HttpResponse("OK")
    return HttpResponse("false")


class ChangeDetailExportView(View):

    @staticmethod
    def get(request, order_detail_id):
        headers = [u'商品编码', u'供应商编码', u'商品名称', u'图片地址', u'规格',
                   u'购买数量', u'买入价格', u'单项价格', u'已入库数', u'次品数']
        order_list = OrderList.objects.get(id=order_detail_id)
        order_details = OrderDetail.objects.filter(orderlist_id=order_detail_id)
        items = []
        for o in order_details:
            item = model_to_dict(o)
            item['pic_path'] = Product.objects.get(id=o.product_id).pic_path
            item['supplier_outer_id'] = ProductSku.objects.get(
                id=o.chichu_id).get_supplier_outerid()
            items.append(item)

        items = [map(unicode, [i['outer_id'], i['supplier_outer_id'], i['product_name'],
                  i['pic_path'], i['product_chicun'], i['buy_quantity'],
                  i['buy_unitprice'], i['total_price'], i['arrival_quantity'], i['inferior_quantity']]) for i in items]
        sum_of_total_price = round(sum(map(lambda x: float(x[-3]), items)), 2)
        items.append([''] * 6 + [u'总计', unicode(sum_of_total_price)] + [''] * 2)
        items.insert(0, headers)
        buff = StringIO()
        is_windows = request.META['HTTP_USER_AGENT'].lower().find('windows') >-1
        writer = CSVUnicodeWriter(buff, encoding=is_windows and 'gbk' or 'utf-8')
        writer.writerows(items)
        response = HttpResponse(buff.getvalue(), mimetype='application/octet-stream')
        response['Content-Disposition'] = 'attachment;filename=dinghuodetail-%s.csv' % order_detail_id
        return response
