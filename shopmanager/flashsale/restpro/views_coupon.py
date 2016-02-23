# coding=utf-8
from flashsale.pay.models_coupon_new import UserCoupon, CouponsPool, CouponTemplate
from rest_framework import viewsets
from . import serializers
from rest_framework import authentication
from rest_framework import permissions
from rest_framework import renderers
from django.shortcuts import get_object_or_404
from flashsale.pay.models import Customer
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import APIException
from shopback.items.models import Product
import datetime


class UserCouponsViewSet(viewsets.ModelViewSet):
    """
    - {prefix}/method: get 获取用户惠券(默认为有效且没有过期的优惠券)
    - {prefix}/list_past_coupon method:get 获取用户已经过期的优惠券
        -  return:
            `id`:优惠券id <br>`coupon_no:`优惠券券池号码<br>
            `title`: 优惠券模板定义的标题
            `status:` 优惠券状态　0：未使用，１:已经使用， 2:冻结中<br>
            `poll_status:` 券池发放状态：１:已经发放，0：未发放，2:已经过期<br>
            `coupon_type:` 优惠券类型：RMB118:"二期代理优惠券" ,POST_FEE:"退货补邮费", C150_10:"满150减10", C259_20:"满259减20"<br>
            `sale_trade:`  绑定交易id：购买交易的id<br>
            `customer:`　对应的客户id<br>
            `coupon_value:` 优惠券对应的面值<br>
            `valid:`　优惠券的有效性（true or false）<br> `title:`　优惠券标题<br>
            `created:`　创建时间<br> `deadline:`　截止时间<br>
            `use_fee:` 满单额（即满多少可以使用）

    - {prefix}/method: post 创建用户优惠券

        `arg`: coupon_type  优惠券类型
        `C150_10:` 满150减10
        `C259_20:` 满259减20

        -  return:
        `创建受限` {'res':'limit'}
        `创建成功` {'res':'success'}
        `暂未发放`{'res':'not_release'}
    """

    queryset = UserCoupon.objects.all()
    serializer_class = serializers.UsersCouponSerializer
    authentication_classes = (authentication.SessionAuthentication, authentication.BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated, )
    renderer_classes = (renderers.JSONRenderer, renderers.BrowsableAPIRenderer,)

    def get_owner_queryset(self, request):
        customer = get_object_or_404(Customer, user=request.user)
        return self.queryset.filter(customer=customer.id)

    def list_valid_coupon(self, queryset, valid=True):
        """ 过滤模板是否有效状态 """
        queryset = queryset.filter(cp_id__template__valid=valid)
        return queryset

    def list_unpast_coupon(self, queryset, status=CouponsPool.RELEASE):
        """ 过滤券池状态 """
        queryset = queryset.filter(cp_id__status=status)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_owner_queryset(request))
        queryset = self.list_valid_coupon(queryset, valid=True)
        queryset = self.list_unpast_coupon(queryset, status=CouponsPool.RELEASE)
        queryset = queryset.order_by('created')[::-1]  # 时间排序
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def list_past_coupon(self, request):
        queryset = self.filter_queryset(self.get_owner_queryset(request))
        queryset = self.list_unpast_coupon(queryset, status=CouponsPool.PAST)
        queryset = queryset.order_by('created')[::-1]  # 时间排序
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """　根据参数生成不同类型的优惠券　"""
        content = request.REQUEST
        # if content:
        # return Response({"res": "not_release"})
        try:
            template_id = int(content.get("template_id", None))
        except TypeError:
            return Response({"res": "not_release"})
        try:
            customer = Customer.objects.get(user=request.user)
            if template_id:  # 根据模板id发放
                uc = UserCoupon()
                cus = {"buyer_id": customer.id, "template_id": template_id}
                release_res = uc.release_by_template(**cus)
                return Response({"res": release_res})
        except Customer.DoesNotExist:
            return Response({"res": "cu_not_fund"})
        else:
            return Response({"res": "not_release"})

    @detail_route(methods=["post"])
    def choose_coupon(self, request, pk=None):
        content = request.REQUEST
        price = float(content.get("price", 0))
        item = int(content.get("item_id", 0))
        try:
            pro = Product.objects.get(id=item)
            if item and (pro.details.is_seckill or str(pro.name).startswith("秒杀")):
                raise APIException(u"秒杀产品不支持使用优惠券")
        except Product.DoesNotExist:
            pass
        coupon_id = pk  # 获取order_id
        queryset = self.filter_queryset(self.get_owner_queryset(request)).filter(id=coupon_id)
        coupon = queryset.get(id=pk)
        try:
            coupon.check_usercoupon()  # 验证优惠券
            coupon.cp_id.template.usefee_check(price)
        except Exception, exc:
            raise APIException(u"错误:%s" % exc.message)
        return Response({"res": "ok"})


class CouponTemplateViewSet(viewsets.ModelViewSet):
    queryset = CouponTemplate.objects.all()
    serializer_class = serializers.CouponTemplateSerializer
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)  # 这里使用只读的权限
    renderer_classes = (renderers.JSONRenderer, renderers.BrowsableAPIRenderer,)

    def get_useful_template_query(self):
        # 点击方式领取的　有效的　在预置天数内的优惠券
        tpls = self.queryset.filter(way_type=CouponTemplate.CLICK_WAY, valid=True).exclude(
            type__in=(CouponTemplate.RMB118, CouponTemplate.POST_FEE_5, CouponTemplate.POST_FEE_10,
                      CouponTemplate.POST_FEE_15, CouponTemplate.POST_FEE_20))
        temps = []
        now = datetime.datetime.now()
        for tpl in tpls:
            # 如果现在的时间是在截止日期减去预置天数后日期之间则加入集合
            time_start = tpl.deadline - datetime.timedelta(days=tpl.preset_days)
            if now >= time_start and now <= tpl.deadline:
                temps.append(tpl)
        return temps

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_useful_template_query())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        return Response()


