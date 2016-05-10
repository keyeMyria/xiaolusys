# coding=utf-8
"""
模板：负责优惠券的定义（用途，价值，标题） 普通类型模板只能领取一张
分享批次：负责分享时候生成批次记录,绑定交易,用户,使用模板
用户：负责记录用户优惠券持有状态,使用价值等信息
"""
import datetime

from django.db import models

from flashsale.pay.options import uniqid
from core.models import BaseModel
from core.fields import JSONCharMyField
from flashsale.coupon.managers import UserCouponManager
from managers import OrderShareCouponManager


def default_template_extras():
    return {
        'release': {
            'use_min_payment': 500,  # 满多少可以使用
            'release_min_payment': 50,  # 满多少可以发放
            'use_after_release_days': 0,  # 发放多少天后可用
            'limit_after_release_days': 30,  # 发放多少天内可用
            'share_times_limit': 20  # 分享链接被成功领取的优惠券次数
        },
        'randoms': {'min_val': 0, 'max_val': 1},  # 随机金额范围
        'scopes': {'product_ids': '', 'category_ids': ''},  # 使用范围
        'templates': {'post_img': ''}  # 优惠券模板
    }


class CouponTemplate(BaseModel):
    """ 优惠券模板 """

    TYPE_NORMAL = 1
    TYPE_ORDER_SHARE = 2
    TYPE_MAMA_INVITE = 3
    TYPE_COMPENSATE = 4
    TYPE_ORDER_BENEFIT = 5
    TYPE_ACTIVE_SHARE = 6
    COUPON_TYPES = (
        (TYPE_NORMAL, u"普通类型"),  # 一般点击类型,或者普通发放类型
        (TYPE_ORDER_BENEFIT, u"下单红包"),  # 用户购买商品后发放
        (TYPE_ORDER_SHARE, u"订单分享"),  # 用户购买商品后分享给其他人领取
        (TYPE_MAMA_INVITE, u"推荐专享"),  # 在代理的专属链接购买商品后,给代理发放的类型
        (TYPE_COMPENSATE, u"售后补偿"),  # 不邮费等售后服务发放
        (TYPE_ACTIVE_SHARE, u"活动分享")  # 不邮费等售后服务发放
    )

    TARGET_ALL = 1
    TARGET_VIP = 2
    TARGET_A = 3
    # 这里注意下类型对应在xiaolumm模块的代理级别
    TARGET_TYPES = ((TARGET_ALL, u"所有用户"),
                    (TARGET_VIP, u"VIP类代理"),
                    (TARGET_A, u"A类代理"))

    SCOPE_OVERALL = 1
    SCOPE_CATEGORY = 2
    SCOPE_PRODUCT = 3
    SCOPE_TYPES = ((SCOPE_OVERALL, u"全场通用"),
                   (SCOPE_CATEGORY, u"类目专用"),
                   (SCOPE_PRODUCT, u"商品专用"))

    CREATE = 0
    SENDING = 1
    FINISHED = 2
    CANCEL = 3
    STATUS_CHOICES = ((CREATE, u'未发放'),  # 定义模板后没有发放 待用
                      (SENDING, u'发放中'),  # 模板正在使用中
                      (FINISHED, u'已结束'),  # 正常发放后结束发放
                      (CANCEL, u'已取消'),)  # 发放中到取消状态取消发放

    title = models.CharField(max_length=64, verbose_name=u"优惠券标题")
    description = models.CharField(max_length=128, verbose_name=u"使用说明")
    value = models.FloatField(default=1.0, verbose_name=u"优惠券价值")

    is_random_val = models.BooleanField(default=False, db_index=True, verbose_name=u"金额随机")
    prepare_release_num = models.IntegerField(default=0, verbose_name=u"计划发放数量")
    is_flextime = models.BooleanField(default=False, db_index=True, verbose_name=u"弹性有效时间")

    release_start_time = models.DateTimeField(blank=True, null=True, verbose_name=u'开始发放的时间')
    release_end_time = models.DateTimeField(blank=True, null=True, verbose_name=u'结束发放的时间')
    use_deadline = models.DateTimeField(blank=True, null=True, verbose_name=u'截止使用的时间')

    has_released_count = models.IntegerField(default=0, verbose_name=u"已领取数量")
    has_used_count = models.IntegerField(default=0, verbose_name=u"已使用数量")

    coupon_type = models.IntegerField(default=TYPE_NORMAL, choices=COUPON_TYPES, verbose_name=u"优惠券类型")
    target_user = models.IntegerField(default=TARGET_ALL, choices=TARGET_TYPES, verbose_name=u"目标用户")
    scope_type = models.IntegerField(default=SCOPE_OVERALL, choices=SCOPE_TYPES, verbose_name=u"使用范围")

    status = models.IntegerField(default=CREATE, choices=STATUS_CHOICES, verbose_name=u"状态")
    extras = JSONCharMyField(max_length=512, blank=True, null=True,
                             default=default_template_extras,
                             verbose_name=u"附加信息")

    class Meta:
        db_table = "flashsale_coupon_template"
        app_label = 'coupon'
        verbose_name = u"特卖/优惠券/模板"
        verbose_name_plural = u"特卖/优惠券/模板列表"

    def __unicode__(self):
        return '<%s,%s>' % (self.id, self.title)

    @property
    def share_times_limit(self):
        return self.extras['release']['share_times_limit']

    @property
    def post_img(self):
        return self.extras['templates']['post_img']

    @property
    def limit_after_release_days(self):
        """ 发放后多少天内可用 """
        return self.extras['release']['limit_after_release_days']

    @property
    def use_after_release_days(self):
        """ 发放多少天后可用 """
        return self.extras['release']['use_after_release_days']

    @property
    def use_min_payment(self):
        """ 最低购买金额 """
        return self.extras['release']['use_min_payment']

    @property
    def bind_category_ids(self):
        """ 绑定产品类目 """
        return self.extras['scopes']['category_ids']

    @property
    def bind_product_ids(self):
        """ 绑定产品产品 """
        return self.extras['scopes']['product_ids']

    @property
    def min_val(self):
        """ 随机最小值 """
        return self.extras['randoms']['min_val']

    @property
    def max_val(self):
        """ 随机最大值 """
        return self.extras['randoms']['max_val']

    def template_valid_check(self):
        """
        模板检查, 不在发放中 和发放结束状态的优惠券视为无效优惠券
        """
        if self.status not in (CouponTemplate.SENDING, CouponTemplate.FINISHED):
            raise AssertionError(u"无效优惠券")
        return self

    def template_valid(self):
        """ 模板是否有效 """
        if self.status in (CouponTemplate.SENDING, CouponTemplate.FINISHED):
            return True
        return False

    def use_fee_desc(self):
        """ 满单额描述 """
        return "满{0}可用".format(self.use_min_payment)

    def usefee_check(self, fee):
        """
        满单额条件检查　
        :param fee 交易金额
        """
        if self.use_min_payment == 0:
            return
        elif self.use_min_payment > fee:
            raise AssertionError(u'该优惠券满%s元可用' % self.use_min_payment)

    def check_date(self):
        """ 检查有效天数（匹配截止日期） 返回有效的开始时间和结束时间 """
        # 判断当前时间是否在　有效时间内
        now = datetime.datetime.now()
        if self.release_start_time <= now <= self.use_deadline:
            return  # 在正常时间内
        raise AssertionError(u'%s至%s可以使用' % (self.start_use_time, self.use_deadline))

    def check_category(self, product_ids=None):
        """ 可用分类检查 """
        category_ids = self.bind_category_ids
        if not category_ids:  # 没有设置分类限制信息　则为全部分类可以使用
            return
        from shopback.items.models import Product

        tpl_categorys = category_ids.strip().split(',') if category_ids else []

        buy_pros_categorys = Product.objects.filter(id__in=product_ids).values('category_id')
        buy_category_ids = [str(i['category_id']) for i in buy_pros_categorys]

        set_tpl_categorys = set(tpl_categorys)
        set_category = set(buy_category_ids)
        if len(set_tpl_categorys & set_category) == 0:  # 比较分类 如果没有存在的分类则报错
            raise AssertionError(u'该品类不支持使用优惠券')
        return

    def check_bind_pros(self, product_ids=None):
        """ 检查绑定的产品 """
        tpl_product_ids = self.bind_product_ids  # 设置的绑定的产品
        tpl_bind_pros = tpl_product_ids.strip().split(',') if tpl_product_ids else []  # 绑定的产品list
        if not tpl_bind_pros != []:  # 如果优惠券没有绑定产品
            self.check_category(product_ids)  # 没有限制产品则检查分类限制
            return
        product_str_ids = [str(i) for i in product_ids]
        tpl_binds = set(tpl_bind_pros)
        pro_set = set(product_str_ids)
        if len(tpl_binds & pro_set) == 0:
            raise AssertionError(u'该产品不支持使用优惠券')
        # 检查产品后检查分类(检查设置了绑定产品并且绑定了类目的情况)
        self.check_category(product_ids)


def default_share_extras():
    return {
        'user_info': {'id': None, 'nick': '', 'thumbnail': ''},
        "templates": {"post_img": '', "description": ''}
    }


class OrderShareCoupon(BaseModel):
    WX = u'wx'
    PYQ = u'pyq'
    QQ = u'qq'
    QQ_SPA = u'qq_spa'
    SINA = u'sina'
    WAP = u'wap'
    PLATFORM = ((WX, u"微信好友"), (PYQ, u"朋友圈"), (QQ, u"QQ好友"),
                (QQ_SPA, u"QQ空间"), (SINA, u"新浪微博"), (WAP, u'wap'))
    SENDING = 0
    FINISHED = 1
    STATUS_CHOICES = (
        (SENDING, u'发放中'),
        (FINISHED, u'已结束'))
    template_id = models.IntegerField(db_index=True, verbose_name=u"模板ID")
    share_customer = models.IntegerField(db_index=True, verbose_name=u'分享用户')
    uniq_id = models.CharField(max_length=32, unique=True, verbose_name=u"唯一ID")  # 交易的tid

    release_count = models.IntegerField(default=0, verbose_name=u"领取次数")  # 该分享下 优惠券被领取成功次数
    has_used_count = models.IntegerField(default=0, verbose_name=u"使用次数")  # 该分享下产生优惠券被使用的次数
    limit_share_count = models.IntegerField(default=0, verbose_name=u"最大领取次数")

    platform_info = JSONCharMyField(max_length=128, blank=True, default='{}', verbose_name=u"分享到平台记录")
    share_start_time = models.DateTimeField(blank=True, verbose_name=u"分享开始时间")
    share_end_time = models.DateTimeField(blank=True, db_index=True, verbose_name=u"分享截止时间")

    # 用户点击分享的时候 判断如果达到最大分享次数了 修改该状态到分享结束
    status = models.IntegerField(default=SENDING, db_index=True, choices=STATUS_CHOICES, verbose_name=u"状态")
    extras = JSONCharMyField(max_length=1024, default=default_share_extras, blank=True, null=True,
                             verbose_name=u"附加信息")
    objects = OrderShareCouponManager()

    class Meta:
        db_table = "flashsale_coupon_share_batch"
        app_label = 'coupon'
        verbose_name = u"特卖/优惠券/订单分享表"
        verbose_name_plural = u"特卖/优惠券/订单分享列表"

    def __unicode__(self):
        return "<%s,%s>" % (self.id, self.template_id)

    @property
    def nick(self):
        """分享者昵称"""
        return self.extras['user_info']['nick']

    @property
    def thumbnail(self):
        """分享者的头像"""
        return self.extras['user_info']['thumbnail']

    @property
    def post_img(self):
        """模板的图片链接"""
        return self.extras['templates']['post_img']

    @property
    def description(self):
        """模板的描述"""
        return self.extras['templates']['description']


def default_coupon_no():
    return uniqid('%s%s' % ('yhq', datetime.datetime.now().strftime('%y%m%d')))


def default_coupon_extras():
    return {'user_info': {'id': None, 'nick': '', 'thumbnail': ''}}


class UserCoupon(BaseModel):
    TYPE_NORMAL = 1
    TYPE_ORDER_SHARE = 2
    TYPE_MAMA_INVITE = 3
    TYPE_COMPENSATE = 4
    TYPE_ORDER_BENEFIT = 5
    TYPE_ACTIVE_SHARE = 6
    COUPON_TYPES = (
        (TYPE_NORMAL, u"普通类型"),  # 一般点击类型,或者普通发放类型
        (TYPE_ORDER_BENEFIT, u"下单红包"),  # 用户购买商品后发放
        (TYPE_ORDER_SHARE, u"订单分享"),  # 用户购买商品后分享给其他人领取
        (TYPE_MAMA_INVITE, u"推荐专享"),  # 在代理的专属链接购买商品后,给代理发放的类型
        (TYPE_COMPENSATE, u"售后补偿"),  # 不邮费等售后服务发放
        (TYPE_ACTIVE_SHARE, u"活动分享")  # 不邮费等售后服务发放
    )

    UNUSED = 0
    USED = 1
    FREEZE = 2
    PAST = 3
    USER_COUPON_STATUS = ((UNUSED, u"未使用"), (USED, u"已使用"), (FREEZE, u"冻结中"), (PAST, u"已经过期"))

    WX = u'wx'
    PYQ = u'pyq'
    QQ = u'qq'
    QQ_SPA = u'qq_spa'
    SINA = u'sina'
    WAP = u'wap'
    TMP = u'tmp'
    PLATFORM = ((WX, u"微信好友"),
                (PYQ, u"朋友圈"),
                (QQ, u"QQ好友"),
                (QQ_SPA, u"QQ空间"),
                (SINA, u"新浪微博"),
                (WAP, u'wap'),
                (TMP, u'临时表'))

    template_id = models.IntegerField(db_index=True, verbose_name=u"优惠券id")
    title = models.CharField(max_length=64, verbose_name=u"优惠券标题")
    coupon_type = models.IntegerField(default=TYPE_NORMAL, choices=COUPON_TYPES, verbose_name=u"优惠券类型")

    customer_id = models.IntegerField(db_index=True, verbose_name=u"顾客ID")
    share_user_id = models.IntegerField(db_index=True, blank=True, null=True, verbose_name=u"分享用户ID")
    order_coupon_id = models.IntegerField(db_index=True, blank=True, null=True, verbose_name=u"订单优惠券分享ID")

    coupon_no = models.CharField(max_length=32, unique=True,
                                 default=default_coupon_no, verbose_name=u"优惠券号码")
    value = models.FloatField(verbose_name=u"优惠券价值")

    trade_tid = models.CharField(max_length=32, db_index=True, blank=True, null=True, verbose_name=u"绑定交易tid")
    # finished_time 保存优惠券被使用掉的时间
    finished_time = models.DateTimeField(db_index=True, blank=True, null=True, verbose_name=u"使用时间")
    start_use_time = models.DateTimeField(db_index=True, verbose_name=u"开始时间")
    expires_time = models.DateTimeField(db_index=True, verbose_name=u"过期时间")

    ufrom = models.CharField(max_length=8, choices=PLATFORM, db_index=True, blank=True, verbose_name=u'领取平台')
    uniq_id = models.CharField(unique=True, max_length=32,  # template_id_customer_id_order_coupon_id_(number_of_tpl)
                               verbose_name=u"优惠券唯一标识")
    status = models.IntegerField(default=UNUSED, choices=USER_COUPON_STATUS, verbose_name=u"使用状态")
    extras = JSONCharMyField(max_length=1024, default=default_coupon_extras, blank=True, null=True,
                             verbose_name=u"附加信息")
    objects = UserCouponManager()

    class Meta:
        db_table = "flashsale_user_coupon"
        app_label = 'coupon'
        verbose_name = u"特卖/优惠券/用户优惠券表"
        verbose_name_plural = u"特卖/优惠券/用户优惠券列表"

    def __unicode__(self):
        return "<%s,%s>" % (self.id, self.customer_id)

    def self_template(self):
        tpl = CouponTemplate.objects.get(id=self.template_id)
        return tpl

    def share_record(self):
        """ 优惠券来自与那个分享(如果是从分享来的话) """
        return OrderShareCoupon.objects.filter(id=self.order_coupon_id).first()

    def is_valid_template(self):
        """ 模板有效性 """
        tpl = self.self_template()
        return True if tpl.template_valid_check() else False

    def min_payment(self):
        """ 最低使用费用(满单额) """
        tpl = self.self_template()
        return tpl.use_min_payment

    def coupon_use_fee_des(self):
        """ 满单额描述 """
        min_payment = self.min_payment()
        return u"满%s可用" % min_payment

    def scope_type_desc(self):
        """ 使用范围描述 """
        tpl = self.self_template()
        return tpl.get_scope_type_display()

    def coupon_basic_check(self):
        """
        日期检测 & 状态检查
        """
        now = datetime.datetime.now()
        coupon = self.__class__.objects.get(id=self.id)
        if coupon.status == UserCoupon.USED:
            raise AssertionError(u"优惠券已使用")
        elif coupon.status == UserCoupon.FREEZE:
            raise AssertionError(u"优惠券已冻结")
        elif coupon.status == UserCoupon.PAST:
            raise AssertionError(u"优惠券已过期")
        if not (now <= coupon.expires_time):
            raise AssertionError(u"使用日期错误")
        return coupon

    def check_user_coupon(self, product_ids=None, use_fee=None):
        """  用户优惠券检查是否可用 """
        tpl = CouponTemplate.objects.get(id=self.template_id)
        tpl.check_bind_pros(product_ids=product_ids)  # 绑定产品检查
        tpl.template_valid_check()  # 模板有效性检查
        tpl.usefee_check(use_fee)  # 优惠券状态检查
        self.coupon_basic_check()  # 基础检查
        return

    def use_coupon(self, trade_tid):
        """ 使用优惠券 """
        from flashsale.coupon.tasks import task_update_coupon_use_count

        coupon = self.__class__.objects.get(id=self.id)
        coupon.coupon_basic_check()  # 基础检查
        coupon.status = self.USED
        coupon.save()
        task_update_coupon_use_count.delay(coupon, trade_tid)

    def freeze_coupon(self):
        """ 冻结优惠券 """
        coupon = self.__class__.objects.get(id=self.id)
        if coupon.status != UserCoupon.UNUSED:
            raise AssertionError(u"优惠券不在未使用状态,冻结失败")
        self.status = self.FREEZE
        self.save()

    def unfreeze_coupon(self):
        """ 解冻优惠券 """
        coupon = self.__class__.objects.get(id=self.id)
        if coupon.status != UserCoupon.FREEZE:
            raise AssertionError(u"优惠券不在冻结状态,解冻出错")
        self.status = self.UNUSED
        self.save()


class TmpShareCoupon(BaseModel):
    mobile = models.CharField(max_length=11, db_index=True, verbose_name=u'手机号')
    share_coupon_id = models.CharField(db_index=True, max_length=32, verbose_name=u"分享uniq_id")
    status = models.BooleanField(default=False, db_index=True, verbose_name=u'是否领取')

    class Meta:
        unique_together = ('mobile', 'share_coupon_id')  # 一个分享 一个手机号只能领取一次
        db_table = "flashsale_user_tmp_coupon"
        app_label = 'coupon'
        verbose_name = u"特卖/优惠券/用户临时优惠券表"
        verbose_name_plural = u"特卖/优惠券/用户临时优惠券列表"

    def __unicode__(self):
        return "<%s,%s>" % (self.id, self.mobile)
