#-*- encoding:utf8 -*-
import json
import time
import urlparse
import datetime
from django.conf import settings
from django.db import IntegrityError,models
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.views.generic import View
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder

from shopback.items.models import Product,ProductSku,ProductCategory
from .models import SaleTrade,SaleOrder,genUUID,Customer
from .tasks import confirmTradeChargeTask
from flashsale.xiaolumm.models import CarryLog,XiaoluMama
import pingpp
import logging
logger = logging.getLogger('django.request')

import re
UUID_RE = re.compile('^[a-zA-Z0-9-]{21,36}$')


class ProductNotOnSale(Exception):
    pass


class PINGPPChargeView(View):
    
    def createSaleTrade(self,customer,form,charge=None,**kwargs):
        
        product = Product.objects.get(pk=form.get('item_id'))
        sku = ProductSku.objects.get(pk=form.get('sku_id'),product=product)
        total_fee = sku.std_sale_price * int(form.get('num'))
#         if float(form['payment']) < total_fee:
#             raise Exception(u'订单提交金额与商品价格差异')
        
        sale_trade = SaleTrade.objects.create(
                                 tid=form.get('uuid'),
                                 buyer_id=customer.id,
                                 buyer_nick=customer.nick,
                                 channel=form.get('channel'),
                                 receiver_name=form.get('receiver_name'),
                                 receiver_state=form.get('receiver_state'),
                                 receiver_city=form.get('receiver_city'),
                                 receiver_district=form.get('receiver_district'),
                                 receiver_address=form.get('receiver_address'),
                                 receiver_zip=form.get('receiver_zip'),
                                 receiver_phone=form.get('receiver_phone',''),
                                 receiver_mobile=form.get('receiver_mobile'),
                                 buyer_message=form.get('buyer_message',''),
                                 payment=float(form.get('payment')),
                                 total_fee=total_fee,
                                 post_fee=form.get('post_fee'),
                                 discount_fee=form.get('discount_fee'),
                                 charge=charge and charge['id'] or '',
                                 status=SaleTrade.WAIT_BUYER_PAY,
                                 openid=customer.openid
                                 )
        sale_order_no = form.get('uuid').replace('FD','FO')
        SaleOrder.objects.create(oid=sale_order_no,
                                 sale_trade=sale_trade,
                                 item_id=form.get('item_id'),
                                 sku_id=form.get('sku_id'),
                                 num=form.get('num'),
                                 outer_id=product.outer_id,
                                 outer_sku_id=sku.outer_id,
                                 title=product.name,
                                 payment=float(form.get('payment')),
                                 total_fee=total_fee,
                                 pic_path=product.pic_path,
                                 sku_name=sku.properties_alias,
                                 status=SaleTrade.WAIT_BUYER_PAY)
        
        return sale_trade
    
    def post(self, request, *args, **kwargs):
        
        form = request.POST
        logger.debug('PINGPP CHARGE REQ: %s'%form)
        err_msg = ''
        try:
            channel = form.get('channel')
            user = request.user
            customer = Customer.getCustomerByUser(user)
            if not customer:
                raise Exception(u'用户未找到')
            
            order_no = form.get('uuid')
            if not UUID_RE.match(order_no):
                raise Exception(u'参数错误!')
            
            buy_num =  int(form.get('num'))
            payment = int(float(form.get('payment')) * 100)
            product = Product.objects.get(pk=form.get('item_id'))
            if (product.shelf_status != Product.UP_SHELF or
                 product.status != Product.NORMAL):
                raise ProductNotOnSale(u'商品已被挤下架啦！')
            
            try:
                xlmm = XiaoluMama.objects.get(openid=customer.unionid)
            except XiaoluMama.DoesNotExist:
                xlmm = None
            
            sku = ProductSku.objects.get(pk=form.get('sku_id'),product=product)

            discount_fee = sku.calc_discount_fee(xlmm=xlmm)
            real_fee = int(sku.agent_price * buy_num * 100) - int(discount_fee * 100)
            
            assert buy_num > 0 and sku.real_remainnum >= buy_num ,u'商品已抢光'
            
            discount_fee = sku.calc_discount_fee(xlmm=xlmm)
            real_fee = int(sku.agent_price * buy_num * 100) - int(discount_fee * 100)

            assert payment > 0 and payment == real_fee ,u'订单金额有误'
            
            response_charge = None
            if channel == SaleTrade.WALLET:
                
                try:
                    xlmm = XiaoluMama.objects.get(openid=customer.unionid)
                except XiaoluMama.DoesNotExist:
                    raise Exception(u'小鹿妈妈未找到')
                
                strade = self.createSaleTrade(customer,form)
                
                urows = XiaoluMama.objects.filter(openid=customer.unionid,
                                                 cash__gte=payment).update(cash=models.F('cash')-payment)
                
                if urows == 0:
                    raise Exception(u'钱包付款失败')
                
                CarryLog.objects.create(xlmm=xlmm.id,
                                        order_num=strade.id,
                                        buyer_nick=strade.buyer_nick,
                                        value=payment,
                                        log_type=CarryLog.ORDER_BUY,
                                        carry_type=CarryLog.CARRY_OUT)
                
                #确认付款后保存
                confirmTradeChargeTask.s(strade.id)()
                
                response_charge = {'channel':channel,'success':True}
                
            else:
                payback_url = urlparse.urljoin(settings.M_SITE_URL,reverse('user_payresult'))
                extra = {}
                if channel == SaleTrade.WX_PUB:
                    extra = {'open_id':customer.openid,'trade_type':'JSAPI'}
                    
                elif channel == SaleTrade.ALIPAY_WAP:
                    extra = {"success_url":payback_url,
                             "cancel_url":payback_url}
                    
                elif channel == SaleTrade.UPMP_WAP:
                    extra = {"result_url":payback_url}
                
                params ={ 'order_no':'%s'%order_no,
                          'app':dict(id=settings.PINGPP_APPID),
                          'channel':channel,
                          'currency':'cny',
                          'amount':'%d'%(float(form['payment'])*100),
                          'client_ip':settings.PINGPP_CLENTIP,
                          'subject':u'小鹿美美平台交易',
                          'body':json.dumps([form.get('item_id'),
                                             form.get('sku_id'),
                                             form.get('num'),
                                             form.get('payment'),
                                             form.get('post_fee')]),
                          'metadata':dict(color='red'),
                          'extra':extra}
                
                response_charge = pingpp.Charge.create(api_key=settings.PINGPP_APPKEY,**params)
            
                strade = self.createSaleTrade(customer,form,charge=response_charge)
                
                logger.debug('CHARGE RESP: %s'%response_charge)
        except IntegrityError:
            err_msg = u'订单已提交'
        except ProductNotOnSale,exc:
            err_msg = exc.message
        except XiaoluMama.MultipleObjectsReturned,exc:
            logger.error(exc.message,exc_info=True)
            err_msg = u'OPENID异常请联系管理'
        except Exception,exc:
            logger.error(exc.message,exc_info=True)
            err_msg = exc.message
        
        if err_msg:
            response_charge = {'errcode':'10001','errmsg':err_msg}

        return HttpResponse(json.dumps(response_charge,cls=DjangoJSONEncoder),content_type='application/json')
    
    get = post
    
from django.core.urlresolvers import reverse
from . import tasks

class PINGPPCallbackView(View):
    
    def post(self, request, *args, **kwargs):
        
        content = request.body 
        logger.debug('pingpp callback:%s'%content )
        try:
            # 读取异步通知数据
            notify   = json.loads(content)
        except:
            return HttpResponse('no params')
        
        response = ''
        # 对异步通知做处理
        if 'object' not in notify:
            response = 'fail'
        else:
            if notify['object'] == 'charge':
                # 开发者在此处加入对支付异步通知的处理代码
                if settings.DEBUG:
                    tasks.notifyTradePayTask(notify)
                else:
                    tasks.notifyTradePayTask.s(notify)()
                
                response = 'success'
            elif notify['object'] == 'refund':
                # 开发者在此处加入对退款异步通知的处理代码
                if settings.DEBUG:
                    tasks.notifyTradeRefundTask(notify)
                else:
                    tasks.notifyTradeRefundTask.s(notify)()
                
                response = 'success'
            else:
                response = 'fail'
        
        return HttpResponse(response)
    
    get = post
    

########## alipay callback ###########
class PayResultView(View):

    def get(self, request, *args, **kwargs):
        
        content = request.REQUEST
        logger.info('pay result:%s'%content )
        
        return HttpResponseRedirect(reverse('user_orderlist'))
    
    
class WXPayWarnView(View):
    
    def post(self, request, *args, **kwargs):
        
        content = request.body
        logger.error('wx warning:%s'%content )
        return HttpResponse('ok')
    
    get = post
    
    
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import authentication
from rest_framework import permissions
from rest_framework.compat import OrderedDict
from rest_framework.renderers import JSONRenderer,TemplateHTMLRenderer,BrowsableAPIRenderer
from rest_framework.views import APIView
from rest_framework import filters

from shopback.items.models import Product,ProductSku
from . import serializes 

class ProductList(generics.ListCreateAPIView):
    
    queryset = Product.objects.order_by('outer_id')
    serializer_class = serializes.ProductSerializer
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer)
    
    template_name = "pay/mindex.html"
    #permission_classes = (permissions.IsAuthenticated,)
    paginate_by = 10
    
    filter_backends = (filters.DjangoFilterBackend,)
    
    filter_fields = (
        'category',
    )
    
    def myfilter_queryset(self,queryset,history,time_line):
        if history == 'none':
            return queryset
        
        today = datetime.date.today()
        if history:
            filter_date = today - datetime.timedelta(days=time_line)
            return queryset.filter(sale_time__gte=filter_date,sale_time__lt=today)
        
        return queryset.filter(sale_time=today)
        
        
    def list(self, request, *args, **kwargs):
        
        content    = request.REQUEST
        time_line  = content.get('time_line','0')
        history    = content.get('history','')
        category   = content.get('category','')
        if not time_line.isdigit() or int(time_line) < 0:
            time_line = 0

        if category != '11' and history == 'none':
            history = ''
            
        time_line = int(time_line)
        
        filter_qs = self.filter_queryset(self.get_queryset())
        filter_qs = filter_qs.filter(status=Product.NORMAL,
                                   shelf_status=Product.UP_SHELF)
        
        fliter_qs = self.myfilter_queryset(filter_qs, history, time_line)
        
        page = self.paginate_queryset(fliter_qs)
        if page is not None:
            if hasattr(self,'get_paginated_response'):
                page_response = self.get_serializer(page, many=True)
                serializer = OrderedDict([
                                ('count', self.paginator.page.paginator.count),
                                ('next', self.paginator.get_next_link()),
                                ('previous', self.paginator.get_previous_link()),
                                ('results', page_response.data)
                            ])
            else:
                serializer = self.get_pagination_serializer(page).data
        else:
            serializer = self.get_serializer(fliter_qs, many=True).data

        return Response({'products':serializer, 'category':category, 
                         'history':history, 'time_line':time_line})
    
    
class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = Product.objects.all()
    serializer_class = serializes.ProductDetailSerializer
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer)
    
    template_name = "pay/mproduct.html"
    #permission_classes = (permissions.IsAuthenticated,)

import urllib
from django.http import HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import render_to_response
from .models_addr import UserAddress
from .views_address import ADDRESS_PARAM_KEY_NAME
from .options import uniqid,getAddressByUserOrID
from flashsale.xiaolumm.models import XiaoluMama

class OrderBuyReview(APIView):

#     authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,BrowsableAPIRenderer)
    template_name = "pay/morder.html"
    
    def post(self, request, format=None):
        
        content = request.REQUEST
        user    = request.user
        
        pid     = content.get('pid',None)
        sid     = content.get('sid',None)
        num     = int(content.get('num','1'))
        addrid  = content.get(ADDRESS_PARAM_KEY_NAME,None)
        
        product = get_object_or_404(Product,pk=pid)
        sku     = get_object_or_404(ProductSku,pk=sid)
        if product.prod_skus.filter(id=sku.id).count() == 0:
            raise Http404

        if not Product.objects.isQuantityLockable(sku,num):
            return render_to_response('pay/mproductexpired.html',{'produt_id':pid}
                                      ,context_instance=RequestContext(request))
        
        product_dict = model_to_dict(product)
        sku_dict     = model_to_dict(sku)
 
        post_fee = 0
        real_fee = float(num * sku.agent_price)
        discount_fee = 0
        payment  = real_fee + post_fee 
        
        customers = Customer.objects.filter(user=user)
        if customers.count() == 0:
            return HttpResponseForbidden('NOT EXIST')
        
        customer  = customers[0]
        address = getAddressByUserOrID(customer,addrid)
        if address:
            address = model_to_dict(address)
        
        abs_url  = request.build_absolute_uri().split('#')[0]
        urlparam = urllib.urlencode({'url':abs_url})
        origin_url = urlparam[len('url='):]
        
        weixin_from = False
        alipay_from = True
        wallet_payable = False
        unionid    = customer.unionid.strip()
        if unionid != '': 
            weixin_from = True
        
#         user_agent = request.META.get('HTTP_USER_AGENT')
#         if (user_agent and user_agent.find('MicroMessenger') > 0 
#             and customer.unionid != 'o29cQs4zgDoYxmSO3pH-x4A7O8Sk'):
#             alipay_from = False
        
        xiaolumms = XiaoluMama.objects.filter(openid=unionid)
        xiaolumm  = None
        if xiaolumms.count() > 0:
            xiaolumm = xiaolumms[0]
            #从新计算订单优惠金额 及 需付金额
            discount_fee = sku.calc_discount_fee(xlmm=xiaolumm)
            payment = payment - discount_fee
            if (xiaolumm.cash > 0 and xiaolumm.cash >= payment * 100 
                and not product.outer_id.startswith('RMB')):
                wallet_payable = True
        
        data = {'product':product_dict,
                'sku':sku_dict,
                'num':num,
                'uuid':uniqid('%s%s'%(SaleTrade.PREFIX_NO,datetime.datetime.now().strftime('%y%m%d'))),
                'real_fee':real_fee,
                'discount_fee':discount_fee,
                'post_fee':post_fee,
                'payment':payment,
                'address':address,
                'origin_url':origin_url,
                'xiaolumm':xiaolumm,
                'wallet_payable':wallet_payable,
                'alipay_from':alipay_from,
                'weixin_from':weixin_from}
        
        return Response(data)
    
    get = post

class UserProfile(APIView):
    
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer)
    template_name = "pay/mprofile.html"
    
    def get(self, request, format=None):

        return Response({})
    
    def post(self, request, format=None):
        
        return Response({})
    
    
class SaleOrderList(APIView):
    
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer)
    template_name = "pay/morderlist.html"
    
    def get(self, request, format=None):
        
        status = request.GET.get('status')
        user = request.user
        customers = Customer.objects.filter(user=user)
        if customers.count() == 0:
            return HttpResponseForbidden('NOT EXIST')
        
        customer   = customers[0]
        trade_list = []
        strades = SaleTrade.normal_objects.filter(buyer_id=customer.id)
        if status:
            strades =  strades.filter(status=status)
            
        for trade in strades:
            serializer_trade = serializes.SampleSaleTradeSerializer(trade)
            trade_list.append(serializer_trade.data)
        
        return Response({'trades':trade_list})
    
    def post(self, request, format=None):
        
        return Response({})
    
    
class SaleOrderDetail(APIView):
    
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer)
    template_name = "pay/morderdetail.html"
    
    def get(self, request,pk, format=None):
        
        user = request.user
        customers = Customer.objects.filter(user=user)
        if customers.count() == 0:
            return HttpResponseForbidden('NOT EXIST')
        
        customer   = customers[0]

        strade = get_object_or_404(SaleTrade,buyer_id=customer.id,pk=pk)
        serializer_trade = serializes.SaleTradeSerializer(strade)

        return Response(serializer_trade.data)
    
    def post(self, request, format=None):
        
        return Response({})
    
    
from shopback.logistics import getLogisticTrace
    
class SaleTradeLogistic(APIView):
    
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer)
    template_name = "pay/mlogistic.html"
    
    def get(self, request,pk, format=None):
        
        user = request.user
        customers = Customer.objects.filter(user=user)
        if customers.count() == 0:
            return HttpResponseForbidden('NOT EXIST')
        
        customer   = customers[0]
        strade = get_object_or_404(SaleTrade,buyer_id=customer.id,pk=pk)
        
        logistic_trace = None
        if strade.logistics_company and strade.out_sid:
            logistic_trace = getLogisticTrace(strade.out_sid,
                                              strade.logistics_company.code)
        
        
        return Response({'logistic_trace':logistic_trace})
    
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Sum
from .models_envelope import Envelop
from shopback.base import log_action, ADDITION, CHANGE
      
class EnvelopConfirmSendView(View):
    
    renderer_classes = (JSONRenderer,)
    
    def post(self, request, *args, **kwargs):
        
        content = request.POST
        origin_url  = content.get('origin_url')
        envelop_ids = content.get('envelop_ids','').split(',')
        secret  = content.get('secret')
        
        admin_email = settings.ADMINS[0][1]
        if secret.strip() != admin_email:
            messages.add_message(request, messages.ERROR, u'请输入正确的红包发送暗号！')
            return redirect(origin_url)
        
        envelop_qs = Envelop.objects.filter(id__in=envelop_ids,status__in=(Envelop.WAIT_SEND,Envelop.FAIL))
        
        try:
            for envelop in envelop_qs:
                envelop.send_envelop()
                log_action(request.user.id,envelop,CHANGE,u'发送红包')
        except Exception,exc:
            messages.add_message(request, messages.ERROR, u'红包发送异常:%s'%(exc.message))
            
        envelop_goodqs = Envelop.objects.filter(id__in=envelop_ids,status=Envelop.CONFIRM_SEND)
        envelop_count = envelop_goodqs.count()
        total_amount  = envelop_goodqs.aggregate(total_amount=Sum('amount')).get('total_amount') or 0
    
        messages.add_message(request, messages.INFO, u'已成功发送 %s 个红包，总金额：%s！'%(envelop_count,total_amount / 100.0))
            
        return redirect(origin_url)
    
#     get = post   
import views_refud_status_check

from qiniu import Auth
access_key = "M7M4hlQTLlz_wa5-rGKaQ2sh8zzTrdY8JNKNtvKN"
secret_key = "8MkzPO_X7KhYQjINrnxsJ2eq5bsxKU1XmE8oMi4x"
bucket_name = "xiaolumm"

class QiniuApi(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (JSONRenderer,)

    def get(self, request):
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name, expires=3600)
        return Response({'uptoken': token})