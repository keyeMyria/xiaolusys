# coding=utf-8
from django.views.generic import View
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
from models_coupon import IntegralLog, Integral, Coupon, CouponPool
import datetime


class CouponPoolView(View):
    def get(self, request):
        deadline = datetime.datetime.today()
        unrelease_soupons = CouponPool.objects.filter(
            coupon_status=CouponPool.UNRELEASE)
        return render_to_response("coupon/create_couponpool.html",
                                  {"unrelease_soupons": unrelease_soupons, "deadline": deadline.strftime("%Y-%m-%d")},
                                  context_instance=RequestContext(request))

    def post(self, request):
        content = request.REQUEST
        nums = content.get('nums', None)
        deadline = content.get('deadline', None)
        values = content.get('values', None)
        co_type = content.get('co_type', None)
        today  = datetime.datetime.today()
        print nums, deadline, values, co_type
        if deadline:
            year, month, day = deadline.split('-')
            deadline_time = datetime.datetime(int(year), int(month), int(day))
            if deadline_time < datetime.datetime.now():
                deadline_time = datetime.datetime(today.year,today.month, today.day,0,0,0) + datetime.timedelta(days=7)
        else:
            deadline_time = datetime.datetime.today() + datetime.timedelta(days=7)

        for i in range(0, int(nums)):
            cou = CouponPool()
            cou.coupon_value = values
            cou.deadline = deadline
            cou.coupon_type = int(co_type)  # 优惠券类型
            cou.save()
        unrelease_soupons = CouponPool.objects.filter(
            coupon_status=CouponPool.UNRELEASE)
        return render_to_response("coupon/create_couponpool.html",
                                  {"unrelease_soupons": unrelease_soupons, "values": values, "nums": nums,
                                   "deadline": deadline_time.strftime("%Y-%m-%d")},
                                  context_instance=RequestContext(request))


def Change_Coupon_Status(request):
    # 点击领取发放的时候   将页面勾选的优惠券发放掉（修改其状态为发放的）
    content = request.REQUEST
    coupon_id = content.get('id', None)
    if coupon_id:
        coupon = CouponPool.objects.get(id=coupon_id)
        data = []
        if coupon.coupon_status == CouponPool.UNRELEASE:
            coupon.coupon_status = CouponPool.RELEASE  # 修改为已经发放
            coupon.save()
            coupon_no = coupon.coupon_no
            coupon_data = {'coupon_no': coupon_no}
            data.append(coupon_data)
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            return HttpResponse('released')
    else:
        return HttpResponse('id_is_null')


from django.core.exceptions import ObjectDoesNotExist
from flashsale.pay.models_user import Customer

import logging


def Coupon_Check(request):
    content = request.REQUEST
    coupon_no = content.get('coupon_no', None)
    if coupon_no:
        try:
            coupon = CouponPool.objects.get(coupon_no=coupon_no)
            # 判断该优惠券有没有被领取
            if coupon.coupon_status == CouponPool.RELEASE:  # 是发放的状态才可以领取
                user_id = request.user.id
                try:
                    cus = Customer.objects.get(user_id=user_id)  # 根据请求找到 平台的用户
                    # 为该用户创建一条 优惠券记录
                    try:
                        # 创建该用户的优惠券之前要修改优惠券的状态
                        coupon.coupon_status = CouponPool.PULLED  # 修改状态为被领取（可以使用）
                        coupon.save()
                        # 创建该用户的优惠券
                        user_coupon, state = Coupon.objects.get_or_create(coupon_user=cus.id,
                                                                          coupon_no=coupon.coupon_no)
                        if state:
                            user_coupon.mobile = cus.mobile
                            user_coupon.save()  # 保存该用户提交的优惠券
                            return HttpResponse("ok")
                        else:
                            return HttpResponse("used")
                    except Exception, exc:
                        log = logging.getLogger('django.request')
                        log.error(exc.message, exc_info=True)
                        return HttpResponse("save error")
                except ObjectDoesNotExist:
                    return HttpResponse("user_not_found")
            else:
                return HttpResponse('not_release')
        except ObjectDoesNotExist:
            return HttpResponse("not_found")
    else:
        return HttpResponse('no_is_null')