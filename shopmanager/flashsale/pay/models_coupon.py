# coding=utf-8
from django.db import models
from shopback.base.models import JSONCharMyField
import datetime
from options import uniqid
import json


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

    @property
    def order_info(self):
        info = json.loads(self.order)
        if isinstance(info, list) and len(info) == 1:
            return json.loads(self.order)[0]
        else:
            return {}


class Coupon(models.Model):
    """
    优惠券只能使用一次，退货不退回使用的优惠券。
    """
    RECEIVE = 0
    USED = 1
    EXPIRED = 2
    COUPON_STATUS = ((RECEIVE, u'已领取'), (USED, u'已使用'), (EXPIRED, u'已过期'))

    coupon_user = models.CharField(max_length=32, db_index=True, verbose_name=u"用户ID")
    coupon_no = models.CharField(max_length=40, default='YH0', verbose_name=u"优惠券号码")
    mobile = models.CharField(max_length=11, db_index=True, blank=True, verbose_name=u'手机')
    trade_id = models.CharField(max_length=40, db_index=True, blank=True, verbose_name=u"交易ID")
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'修改日期')
    status = models.IntegerField(db_index=True, default=RECEIVE, choices=COUPON_STATUS, verbose_name=u'使用状态')

    class Meta:
        unique_together = ('coupon_user', 'coupon_no')
        db_table = "sale_user_coupon_table"
        verbose_name = u"特卖用户/优惠券"
        verbose_name_plural = u"特卖用户/优惠券列表"

    def __unicode__(self):
        return '<%s>' % (self.id)

    def xlmm_Coupon_Create(self, *args, **kwargs):
        """
        :function create the xlmm's coupon
        :arg    unionid
                mobile
                deadline
                coupon_type
                coupon_value
                coupon_user
        :return instance of the coupon
        """
        from flashsale.xiaolumm.models import XiaoluMama

        mobile = kwargs['mobile'] or ''
        unionid = kwargs['unionid'] or ''
        coupon_type = kwargs['coupon_type'] or ''
        coupon_value = kwargs['coupon_value'] or ''
        deadline = kwargs['deadline'] or ''
        coupon_user = kwargs['coupon_user'] or ''
        try:
            xlmm = XiaoluMama.objects.get(models.Q(mobile=mobile) | models.Q(openid=unionid))
        except XiaoluMama.DoesNotExist:
            return
        if xlmm and xlmm.agencylevel == 2 and xlmm.charge_status == XiaoluMama.CHARGED:
            cou_p = CouponPool.objects.create(deadline=deadline, coupon_type=coupon_type,
                                              coupon_value=coupon_value, coupon_status=CouponPool.PULLED)
            self.coupon_user = coupon_user
            self.coupon_no = cou_p.coupon_no
            self.mobile = mobile
            self.save()
        return "%s" % (self.id)

    def lmi118_Xlmm_Coupon(self, buyer_id, trade_id, mobile):
        """
        功能：　代理充值118　送30 满30可用　　优惠券
        参数：　buyer_id　卖家的用户ＩＤ
        """
        cou, state = CouponPool.objects.get_or_create(coupon_type=CouponPool.LIM118,
                                                      coupon_status=CouponPool.RELEASE)
        # 生成优惠券 # 已经发放的
        import logging

        try:
            self.coupon_no = cou.coupon_no
            self.coupon_user = buyer_id
            self.trade_id = trade_id
            self.mobile = mobile
            self.save()
        except Exception, exc:
            log = logging.getLogger('django.request')
            log.error(exc.message, exc_info=True)
        return

    def use_coupon(self):
        # 修改　可用优惠券　到　已经使用
        if self.status == Coupon.RECEIVE:
            self.status = Coupon.USED
            self.save()
            return 'ok'
        else:
            return 'notInStatus'


class CouponPool(models.Model):
    """
    优惠券池
    """
    RELEASE = 0
    UNRELEASE = 1
    PAST = 2
    PULLED = 3
    USED = 4
    COUPON_STATUS = ((RELEASE, u'已发放'), (UNRELEASE, u'未发放'), (PAST, u'过期作废'))
    LIM30 = 1
    LIM300 = 2
    LIM100 = 3
    LIM118 = 4
    POST_FEE = 5
    CO_TYPE = ((LIM30, u"订单满30减3"), (LIM300, u"订单满300减30"), (LIM118, u"妈妈专享 订单满30减30"), (POST_FEE, u"优惠券"))

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
        verbose_name = u"优惠券/模板"
        verbose_name_plural = u"优惠券/模板"

    def __unicode__(self):
        return '<%s>' % (self.coupon_no)


from flashsale.pay.models_coupon_new import UserCoupon, CouponTemplate, CouponsPool

"""
这个是数据库数据迁移的程序片段
关系：
    １　目前数据库中只有，二期代理的类型的优惠券
    ２　在新的 CouponTemplate 中新建代理模板，退货补邮费模板
    ３　将Coupon中的  coupon_user 与 UserCoupon customer　匹配
    　　将使用状态　Coupon的status 与　UserCoupon　status　匹配
"""


def coupon_migration_handler():
    # coupons = Coupon.objects.all()  # 获取原来旧表中的数据
    time_from = datetime.datetime(2015, 9, 8, 9, 0, 0)
    time_to = datetime.datetime(2015, 9, 8, 10, 42, 0, 0)
    coupons = Coupon.objects.filter(created__gte=time_from, created__lte=time_to)  # 获取原来旧表中的数据
    items = 0
    for coupon in coupons:
        customer = coupon.coupon_user
        trade_id = coupon.trade_id
        if coupon.status == Coupon.USED:  # 已使用状态
            new_status = UserCoupon.USED  # 已经使用
        else:
            new_status = UserCoupon.UNUSED  # 没有使用的
        if customer and trade_id:
            tpl = CouponTemplate.objects.get(type=CouponTemplate.RMB118, valid=True)  # 获取：模板采用admin后台手动产生
            try:
                # 如果该用户发放过则不发放
                UserCoupon.objects.get(customer=customer, cp_id__template__type=CouponTemplate.RMB118,
                                       sale_trade=trade_id)
            except UserCoupon.DoesNotExist:
                cou = CouponsPool.objects.create(template=tpl)  # 生成券池数据
                if cou.coupon_nums() > tpl.nums:  # 发放数量大于定义的数量　抛出异常
                    cou.delete()  # 删除create 防止产生脏数据
                    message = u"{0},优惠券发放数量不能大于模板定义数量.".format(tpl.get_type_display())
                    raise Exception(message)
                else:
                    usercou = UserCoupon.objects.create(cp_id=cou, customer=customer, sale_trade=trade_id,
                                                        status=new_status)
                    cou.status = CouponsPool.RELEASE  # 发放后，将状态改为已经发放
                    cou.save()
                    items += 1
