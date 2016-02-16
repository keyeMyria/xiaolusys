# -*- coding:utf8 -*-
import os, settings, urlparse
import datetime
import re
import json
import random

from django.views.generic import View
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework.views import APIView
from rest_framework import permissions, authentication
from rest_framework.renderers import BrowsableAPIRenderer

from flashsale.restpro.options import gen_and_save_jpeg_pic
from core.weixin.mixins import WeixinAuthMixin
from core.weixin.options import set_cookie_openid

from flashsale.pay.models import Customer
from shopapp.weixin.views import get_user_openid, valid_openid
from .models_freesample import XLSampleApply, XLFreeSample, XLSampleSku, XLSampleOrder
from .models import XLInviteCode


def genCode():
    NUM_CHAR_LIST = list('1234567890')
    return ''.join(random.sample(NUM_CHAR_LIST, 7))


def get_active_pros_data():
    free_samples = (1, )
    queryset = XLFreeSample.objects.filter(id__in=free_samples)  # 要加入活动的产品
    data = []
    for sample in queryset:
        dic = model_to_dict(sample, exclude=['id'])
        data.append({"sample": dic,
                     "skus": [model_to_dict(sku, fields=['sku_name', 'sku_code']) for sku in sample.skus.all()]})
    return data


class XLSampleapplyView(WeixinAuthMixin, View):
    xlsampleapply = 'promotion/xlsampleapply.html'

    vipcode_default_message = u'请输入邀请码'
    vipcode_error_message = u'邀请码不正确'
    mobile_default_message = u'请输入手机号'
    mobile_error_message = u'手机号码有误'

    PLANTFORM = ('wxapp', 'pyq', 'qq', 'sinawb', 'web', 'qqspa')

    def get(self, request):
        content = request.REQUEST
        vipcode = content.get('vipcode', None)  # 获取分享用户　用来记录分享状况
        agent = request.META.get('HTTP_USER_AGENT', None)  # 获取浏览器类型
        from_customer = content.get('from_customer', 0)  # 分享人的用户id
        if self.is_from_weixin(request):  # 如果是在微信里面
            openid, unionid = self.get_openid_and_unionid(request)  # 获取用户的openid, unionid
            if not self.valid_openid(openid):  # 若果是无效的openid则跳转到授权页面
                return redirect(self.get_wxauth_redirct_url(request))

        # 商品sku信息  # 获取商品信息到页面
        data = get_active_pros_data()  # 获取活动产品数据
        response = render_to_response(self.xlsampleapply,
                                      {"vipcode": vipcode,
                                       "from_customer": from_customer,
                                       "data": data,
                                       "mobile_message": self.mobile_default_message},
                                      context_instance=RequestContext(request))
        if self.is_from_weixin(request):
            set_cookie_openid(response, self._wxpubid, openid, unionid)

        return response

    def post(self, request):
        content = request.REQUEST
        vmobile = content.get("mobile", None)  # 参与活动的手机号
        vipcode = content.get("vipcode", None)  # 活动邀请码
        from_customer = content.get('from_customer') or 0  # 分享人的用户id
        outer_id = content.get('outer_id', None)
        sku_code = content.get("sku_code", None)  # 产品sku码
        ufrom = content.get("ufrom", None)
        openid = None
        agent = request.META.get('HTTP_USER_AGENT', None)  # 获取浏览器类型
        openid, unionid = self.get_openid_and_unionid(request)  # 获取用户的openid, unionid

        data = get_active_pros_data()  # 获取活动产品数据

        regex = re.compile(r'^1[34578]\d{9}$', re.IGNORECASE)
        mobiles = re.findall(regex, vmobile)
        mobile = mobiles[0] if len(mobiles) >= 1 else None
        if mobile:
            custs = Customer.objects.filter(id=from_customer)  # 用户是否存在
            cust = custs[0] if custs.exists() else ''
            if cust:  # 给分享人（存在）则计数邀请数量
                participates = XLInviteCode.objects.filter(mobile=cust.mobile)
                if participates.exists():
                    participate = participates[0]
                    participate.usage_count += 1
                    participate.save()  # 使用次数累加

            url = '/sale/promotion/appdownload/?vipcode={0}&from_customer={1}'.format(vipcode, from_customer)
            xls = XLSampleApply.objects.filter(outer_id=outer_id, mobile=mobile)  # 记录来自平台设申请的sku选项
            if not xls.exists():  # 如果没有申请记录则创建记录
                sku_code_r = '' if sku_code is None else sku_code
                sample_apply = XLSampleApply()
                sample_apply.outer_id = outer_id
                sample_apply.mobile = mobile
                sample_apply.sku_code = sku_code_r
                sample_apply.vipcode = vipcode
                sample_apply.user_openid = openid
                sample_apply.from_customer = from_customer  # 保存分享人的客户id
                if ufrom in self.PLANTFORM:
                    sample_apply.ufrom = ufrom
                sample_apply.save()

                # 生成自己的邀请码
                expiried = datetime.datetime(2016, 2, 29, 0, 0, 0)
                XLInviteCode.objects.genVIpCode(mobile=mobile, expiried=expiried)

            return redirect(url)  # 跳转到下载页面

        return render_to_response(self.xlsampleapply,
                                  {"vipcode": vipcode, "data": data,
                                   "mobile": vmobile,
                                   "mobile_message": self.mobile_error_message},
                                  context_instance=RequestContext(request))


class APPDownloadView(View):
    """ 下载页面 """
    download_page = 'promotion/download.html'

    def get(self, request):
        content = request.REQUEST
        vipcode = content.get("vipcode", None)  # 活动邀请码
        from_customer = content.get("from_customer", None)  # 分享人的用户id
        return render_to_response(self.download_page,
                                  {"vipcode": vipcode, "from_customer": from_customer},
                                  context_instance=RequestContext(request))


class XlSampleOrderView(View):
    """
    免费申请试用活动，生成正式订单页面
    """
    order_page = 'promotion/xlsampleorder.html'
    share_link = 'sale/promotion/xlsampleapply/?from_customer={customer_id}'
    PROMOTION_LINKID_PATH = 'pmt'

    def get_share_link(self, params):
        link = urlparse.urljoin(settings.M_SITE_URL, self.share_link)
        return link.format(**params)

    def get_promotion_result(self, customer_id, outer_id, mobile):
        """ 返回自己的用户id　　返回邀请结果　推荐数量　和下载数量 """
        applys = XLSampleApply.objects.filter(from_customer=customer_id, outer_id=outer_id)
        promote_count = applys.count()  # 邀请的数量　
        xlcodes = XLInviteCode.objects.filter(mobile=mobile)
        vipcode = None
        if xlcodes.exists():
            vipcode = xlcodes[0].vipcode
        app_down_count = XLSampleOrder.objects.filter(xlsp_apply__in=applys.values('id')).count()  # 下载appd 的数量
        share_link = self.share_link.format(**{'customer_id': customer_id})
        link_qrcode = self.gen_custmer_share_qrcode_pic(customer_id)
        res = {'promote_count': promote_count, 'app_down_count': app_down_count, 'share_link': share_link,
               'link_qrcode': link_qrcode, "vipcode": vipcode}
        return res

    def gen_custmer_share_qrcode_pic(self, customer_id):
        root_path = os.path.join(settings.MEDIA_ROOT, self.PROMOTION_LINKID_PATH)
        if not os.path.exists(root_path):
            os.makedirs(root_path)
        params = {'customer_id': customer_id}
        file_name = 'custm-{customer_id}.jpg'.format(**params)
        file_path = os.path.join(root_path, file_name)

        share_link = self.get_share_link(params)
        if not os.path.exists(file_path):
            gen_and_save_jpeg_pic(share_link, file_path)
        return os.path.join(settings.MEDIA_URL, self.PROMOTION_LINKID_PATH, file_name)

    def handler_with_vipcode(self, vipcode, mobile, outer_id, sku_code, customer):
        xlcodes = XLInviteCode.objects.filter(vipcode=vipcode)
        res = None
        if xlcodes.exists():  # 邀请码对应的邀请人存在
            xlcode = xlcodes[0]
            from_mobile = xlcode.mobile
            customers = Customer.objects.filter(mobile=from_mobile, status=Customer.NORMAL)
            if customers.exists():  # 推荐人用户存在
                from_customer = customers[0].id
                expiried = datetime.datetime(2016, 2, 29, 0, 0, 0)
                # 生成自己的邀请码
                new_vipcode = XLInviteCode.objects.genVIpCode(mobile=mobile, expiried=expiried)
                # 生成自己申请记录
                new_xlapply = XLSampleApply.objects.create(outer_id=outer_id, sku_code=sku_code,
                                                           from_customer=from_customer, mobile=mobile,
                                                           vipcode=new_vipcode,
                                                           status=XLSampleApply.ACTIVED)
                xlcode.usage_count += 1  # 推荐人的邀请码使用次数加１
                xlcode.save()
                # 生成自己的正式订单
                XLSampleOrder.objects.create(xlsp_apply=new_xlapply.id, customer_id=customer.id,
                                             outer_id=outer_id, sku_code=sku_code)
                res = self.get_promotion_result(customer.id, outer_id, mobile)
        return res

    def get(self, request):
        title = "活动正式订单"
        data = get_active_pros_data()  # 获取活动产品数据
        return render_to_response(self.order_page, {"data": data, "title": title},
                                  context_instance=RequestContext(request))

    def post(self, request):
        content = request.REQUEST
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            customer = None
        outer_id = content.get('outer_id', None)
        sku_code = content.get('sku_code', None)
        vipcode = content.get('vipcode', None)

        mobile = customer.mobile if customer else None

        data = get_active_pros_data()  # 获取活动产品数据
        title = "活动正式订单"
        if mobile is None or not (sku_code and outer_id):
            if mobile:
                error_message = "请选择尺寸"
            else:
                error_message = "请验证手机"
            return render_to_response(self.order_page,
                                      {
                                          "data": data,
                                          "title": title,
                                          "error_message": error_message
                                      },
                                      context_instance=RequestContext(request))  # 缺少参数
        xlapplys = XLSampleApply.objects.filter(mobile=mobile, outer_id=outer_id).order_by('-created')
        xlapply = None

        if xlapplys.exists():
            xlapply = xlapplys[0]

        # 获取自己的正式使用订单
        xls_orders = XLSampleOrder.objects.filter(customer_id=customer.id, outer_id=outer_id).order_by('-created')

        if len(xls_orders) >= 1:  # 已经有试用订单
            xls_order = xls_orders[0]
            xls_order.sku_code = sku_code  # 将最后一个的sku修改为当前的sku
            xls_order.save()
        else:  # 没有　试用订单　创建　正式　订单记录
            if xlapply:  # 有　试用申请　记录的
                XLSampleOrder.objects.create(xlsp_apply=xlapply.id, customer_id=customer.id,
                                             outer_id=outer_id, sku_code=sku_code)
                xlapply.status = XLSampleApply.ACTIVED  # 激活预申请中的字段
                xlapply.save()
            else:  # 没有试用申请记录的（返回申请页面链接）　提示
                if vipcode not in (None, ""):  # 有邀请码的情况下 根据邀请码生成用户的申请记录和订单记录
                    res = self.handler_with_vipcode(vipcode, mobile, outer_id, sku_code, customer)
                    return render_to_response(self.order_page, {"res": res}, context_instance=RequestContext(request))

                not_apply_message = "您还没有申请记录,请填写邀请码"
                return render_to_response(self.order_page, {"not_apply": not_apply_message},
                                          context_instance=RequestContext(request))
        res = self.get_promotion_result(customer.id, outer_id, mobile)
        print "debug res:", res
        return render_to_response(self.order_page, {"res": res}, context_instance=RequestContext(request))


class PromotionResult(APIView):
    """
    活动中奖结果展示
    """
    result_page = 'promotion/pmt_result.html'
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.SessionAuthentication, authentication.BasicAuthentication,)
    renderer_classes = (BrowsableAPIRenderer,)

    def get_mobile_show(self, customer):
        mobile = ''.join([customer.mobile[0:3], "****", customer.mobile[7:11]])
        applys = XLSampleApply.objects.filter(from_customer=customer.id, outer_id='90061232563')
        promote_count = applys.count()  # 邀请的数量　
        app_down_count = XLSampleOrder.objects.filter(xlsp_apply__in=applys.values('id')).count()  # 下载appd 的数量
        res = (mobile, promote_count, app_down_count)
        return res

    def get(self, request, *args, **kwargs):
        page = int(kwargs.get('page', 1))
        batch = int(kwargs.get('batch', 1))
        month = int(kwargs.get('month', 1))

        order_list = XLSampleOrder.objects.none()

        if month == 1602 and batch == 1:
            start_time = datetime.datetime(2016, 1, 22)
            order_list = XLSampleOrder.objects.filter(created__gt=start_time)

        num_per_page = 20  # Show 20 contacts per page
        paginator = Paginator(order_list, num_per_page)

        try:
            items = paginator.page(page)
        except PageNotAnInteger:  # If page is not an integer, deliver first page.
            items = paginator.page(1)
        except EmptyPage:  # If page is out of range (e.g. 9999), deliver last page of results.
            items = paginator.page(paginator.num_pages)

        customer_ids = [item.customer_id for item in items]
        wx_users = Customer.objects.filter(id__in=customer_ids)
        items = []
        for user in wx_users:
            items.append(self.get_mobile_show(user))

        total = order_list.count()  # 总条数
        num_pages = paginator.num_pages  # 当前页

        next_page = min(page + 1, num_pages)
        prev_page = max(page - 1, 1)
        res = {"items": items, 'num_pages': num_pages,
               'total': total, 'num_per_page': num_per_page,
               'prev_page': prev_page, 'next_page': next_page,
               'page': page, 'batch': batch, 'month': month}
        response = render_to_response(self.result_page, res, context_instance=RequestContext(request))
        return response

