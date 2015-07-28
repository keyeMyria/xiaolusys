# coding=utf-8
from django.db import models
from shopback.base.models import JSONCharMyField
import datetime
from options import uniqid

"""
用户  积分 + 优惠券  模块
用户ID：SaleTrade 中的  buyer_id  也即是：models_user 中的  Customer  id '客户ID'

"""


class Integral(models.Model):
    integral_user = models.BigIntegerField(null=False, unique=True, db_index=True, verbose_name=u"用户ID")
    integral_value = models.IntegerField(default=0, verbose_name=u"订单积分")
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'修改日期')

    class Meta:
        db_table = "sale_user_integral"
        verbose_name = u"特卖用户/积分"
        verbose_name_plural = u"特卖用户/积分列表"

    def __unicode__(self):
        return '<%s>' % (self.id)


class IntegralLog(models.Model):
    """
    记录用户积分的使用情况
    """
    CONFIRM = 1
    CANCEL = 0
    PENDING = 2
    INTEGRAL_STATUS = ((CONFIRM, u'已确定'), (CANCEL, u'已取消'), (PENDING, u'待确定'))
    ORDER_INTEGRA = 1
    LOG_TYPE = ((ORDER_INTEGRA, u'订单积分'),)
    LOG_IN = 1
    LOG_OUT = 0
    IN_OUT = ((LOG_IN, u'增加积分'), (LOG_OUT, u"减少积分"))

    integral_user = models.BigIntegerField(null=False, db_index=True, verbose_name=u"用户ID")
    order_id = models.BigIntegerField(null=False, db_index=True, verbose_name=u"订单ID")
    mobile = models.CharField(max_length=11, db_index=True, blank=True, verbose_name=u'手机')
    log_value = models.IntegerField(default=0, verbose_name=u'记录积分值')
    log_status = models.IntegerField(choices=INTEGRAL_STATUS, verbose_name=u'记录状态')
    log_type = models.IntegerField(choices=LOG_TYPE, verbose_name=u'积分类型')
    in_out = models.IntegerField(choices=IN_OUT, verbose_name=u'积分收支')
    order = JSONCharMyField(max_length=10240, blank=True,
                            default='[{"order_id":"","pic_link":"","trade_id":"","order_status":""}]',
                            verbose_name=u'订单信息')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'修改日期')

    class Meta:
        unique_together = ('integral_user', 'order_id')
        db_table = "sale_user_integral_log"
        verbose_name = u"特卖用户/积分记录表"
        verbose_name_plural = u"特卖用户/积分记录列表"

    def __unicode__(self):
        return '<%s>' % (self.id)


class Coupon(models.Model):
    """
    优惠券只能使用一次，退货不退回使用的优惠券。
    """
    coupon_user = models.CharField(max_length=32, db_index=True, verbose_name=u"用户ID")
    coupon_no = models.CharField(max_length=40, default='YH0', verbose_name=u"优惠券号码")
    mobile = models.CharField(max_length=11, db_index=True, blank=True, verbose_name=u'手机')
    trade_id = models.CharField(max_length=40, blank=True, verbose_name=u"交易ID")
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'修改日期')

    class Meta:
        unique_together = ('coupon_user', 'coupon_no')
        db_table = "sale_user_coupon_table"
        verbose_name = u"特卖用户/优惠券"
        verbose_name_plural = u"特卖用户/优惠券列表"

    def __unicode__(self):
        return '<%s>' % (self.id)


class CouponPool(models.Model):
    """
    优惠券池
    """
    RELEASE = 0
    UNRELEASE = 1
    PAST = 2
    PULLED = 3
    USED = 4
    COUPON_STATUS = ((RELEASE, u'已发放'), (UNRELEASE, u'未发放'), (PAST, u'过期作废'), (PULLED, u'可以使用'), (USED, u'已经使用'))
    LIM10 = 1
    LIM50 = 2
    LIM100 = 3
    CO_TYPE = ((LIM10, u"满30减3"), (LIM50, u"满300减30"), (LIM100, u"满（待定）"))

    coupon_no = models.CharField(max_length=40, unique=True, default=lambda: uniqid(
        '%s%s' % ('YH', datetime.datetime.now().strftime('%y%m%d'))), verbose_name=u"优惠券号码")
    deadline = models.DateTimeField(verbose_name=u"截止日期")
    coupon_type = models.IntegerField(choices=CO_TYPE, default=1, verbose_name=u"优惠券类型")
    coupon_value = models.FloatField(default=1.0, verbose_name=u"优惠券数值")
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'修改日期')
    coupon_status = models.IntegerField(choices=COUPON_STATUS, default=1, verbose_name=u"优惠券状态")

    class Meta:
        db_table = "sale_user_coupon_pool"
        verbose_name = u"特卖用户/优惠券/发放"
        verbose_name_plural = u"特卖用户/优惠券/发放列表"

    def __unicode__(self):
        return '<%s>' % (self.coupon_no)