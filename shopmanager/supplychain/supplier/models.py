# -*- coding:utf-8 -*-
import json
import time

from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import User

import common.utils
from models_praise import SalePraise
from models_hots import HotProduct

from .managers import SaleSupplierManager
from .models_buyer_group import BuyerGroup


class SaleCategory(models.Model):
    NORMAL = 'normal'
    DELETE = 'delete'

    CAT_STATUS = ((NORMAL, u'正常'),
                  (DELETE, u'删除'))

    SALEPRODUCT_CATEGORY_CACHE_KEY = 'xlmm_saleproduct_category_cache'

    name = models.CharField(max_length=64, blank=True, verbose_name=u'类别名')

    parent_cid = models.IntegerField(null=False, db_index=True, verbose_name=u'父类目ID')

    is_parent = models.BooleanField(default=True, verbose_name=u'父类目')
    status = models.CharField(max_length=7, choices=CAT_STATUS, default=NORMAL, verbose_name=u'状态')
    sort_order = models.IntegerField(default=0, verbose_name=u'优先级')

    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'修改日期')

    class Meta:
        db_table = 'supplychain_sale_category'
        app_label = 'supplier'
        verbose_name = u'特卖/选品类目'
        verbose_name_plural = u'特卖/选品类目列表'

    def __unicode__(self):

        if not self.parent_cid:
            return self.name
        try:
            p_cat = self.__class__.objects.get(id=self.parent_cid)
        except:
            p_cat = u'--'
        return '%s / %s' % (p_cat, self.name)

    @property
    def full_name(self):
        return self.__unicode__()

    @classmethod
    def get_category_names(cls, cid):
        categories = cache.get(cls.SALEPRODUCT_CATEGORY_CACHE_KEY)
        if not categories:
            categories = {}
            for category in cls.objects.filter(
                    status=u'normal').order_by('created'):
                categories[category.id] = {
                    'cid': category.id,
                    'pid': category.parent_cid or 0,
                    'name': category.name
                }
            cache.set(cls.SALEPRODUCT_CATEGORY_CACHE_KEY, categories)
        level_1_category_name, level_2_category_name = ('-',) * 2
        category = categories.get(cid)
        if category:
            pid = category['pid']
            if not pid:
                level_1_category_name = category['name']
            else:
                level_2_category_name = category['name']
                level_1_category_name = (categories.get(pid) or
                                         {}).get('name') or ''
        return level_1_category_name, level_2_category_name


class SaleSupplier(models.Model):
    CHARGED = 'charged'
    UNCHARGE = 'uncharge'
    FROZEN = 'frozen'
    STATUS_CHOICES = (
        (UNCHARGE, u'待接管'),
        (CHARGED, u'已接管'),
        (FROZEN, u'已冻结'),
    )

    LEVEL_BEST = 100
    LEVEL_BETTER = 80
    LEVEL_GOOD = 60
    LEVEL_NORMAL = 50
    LEVEL_INFERIOR = 0
    LEVEL_CHOICES = (
        (LEVEL_BEST, u'特级'),
        (LEVEL_BETTER, u'一级'),
        (LEVEL_GOOD, u'二级'),
        (LEVEL_NORMAL, u'三级'),
        (LEVEL_INFERIOR, u'四级'),
    )

    MANUAL = 'manual'
    MANUALINPUT = 'manualinput'
    TAOBAO = 'taobao'
    TMALL = 'tianmao'
    ZHEBABAI = 'zhe800'
    XIAOHER = 'xiaoher'
    VIP = 'vip'
    JHS = 'jhs'
    BBW = 'bbw'
    PLATFORM_CHOICE = (
        (MANUAL, u'线上联系'),
        (MANUALINPUT, u'线下厂店'),
        (TAOBAO, u'淘宝'),
        (TMALL, u'天猫'),
        (ZHEBABAI, u'折800'),
        (XIAOHER, u'小荷特卖'),
        (VIP, u'唯品会'),
        (JHS, u'聚划算'),
        (BBW, u'贝贝网'),)

    SELECTED = 'selected'
    PRICING = 'pricing'
    STORAGED = 'storaged'
    PASSED = 'passed'
    IGNORED = 'ignored'
    REJECTED = 'rejected'
    PROGRESS_CHOICES = (
        (SELECTED, u'待接洽'),
        (PRICING, u'锁定价格'),
        (STORAGED, u'锁定库存'),
        (PASSED, u'已签合同'),
        (REJECTED, u'淘汰'),
        (IGNORED, u'忽略'),)
    NO_TYPE = 0
    MANUFACTURER = 1
    WHOLESALER = 2
    BRAND_OWNER = 3
    CLOTHING_FACTORY = 4
    SUPPLIER_TYPE = ((NO_TYPE, u'未分类'),
                     (MANUFACTURER, u'生产加工'),
                     (WHOLESALER, u'经销批发'),
                     (BRAND_OWNER, u'品牌'),
                     (CLOTHING_FACTORY, u'源头大厂'))

    WARE_NONE = 0
    WARE_SH = 1
    WARE_GZ = 2
    WARE_CHOICES = ((WARE_NONE, u'未选仓'),
                    (WARE_SH, u'上海仓'),
                    (WARE_GZ, u'广州仓'))

    supplier_name = models.CharField(max_length=64, unique=True, blank=False, verbose_name=u'供应商名')
    supplier_code = models.CharField(max_length=64, blank=True, verbose_name=u'品牌缩写')

    description = models.CharField(max_length=1024, blank=True, verbose_name=u'品牌简介')
    brand_url = models.CharField(max_length=512, blank=True, verbose_name=u'商标图片')
    main_page = models.CharField(max_length=256, blank=True, verbose_name=u'品牌主页')

    platform = models.CharField(max_length=16, blank=True, choices=PLATFORM_CHOICE,
                                default=MANUAL, verbose_name=u'来自平台')

    category = models.ForeignKey(SaleCategory, null=True,
                                 related_name='category_suppliers', verbose_name=u'类别')

    level = models.IntegerField(db_index=True, default=LEVEL_NORMAL, choices=LEVEL_CHOICES, verbose_name=u'等级')
    speciality = models.CharField(max_length=256, blank=True, verbose_name=u'产品特长')
    total_select_num = models.IntegerField(default=0, verbose_name=u'总选款数量')
    total_sale_num = models.FloatField(default=0.0, verbose_name=u'总销售件数')
    total_sale_amount = models.FloatField(default=0.0, verbose_name=u'总销售额')
    total_refund_num = models.IntegerField(default=0, verbose_name=u'总退款件数')
    total_refund_amount = models.FloatField(default=0.0, verbose_name=u'总退款额')
    avg_post_days = models.FloatField(default=0, verbose_name=u'平均发货天数')
    return_goods_limit_days = models.IntegerField(default=20, verbose_name=u'退货截止时间')
    last_select_time = models.DateTimeField(db_index=True, null=True, blank=True, verbose_name=u'最后选款日期')
    last_schedule_time = models.DateTimeField(db_index=True, null=True, blank=True, verbose_name=u'最后上架日期')

    contact = models.CharField(max_length=32, blank=False, verbose_name=u'联系人')
    phone = models.CharField(max_length=32, blank=True, verbose_name=u'电话')
    mobile = models.CharField(max_length=16, blank=False, verbose_name=u'手机')
    fax = models.CharField(max_length=16, blank=True, verbose_name=u'传真')
    zip_code = models.CharField(max_length=16, blank=True, verbose_name=u'其它联系')
    email = models.CharField(max_length=64, blank=True, verbose_name=u'邮箱')

    address = models.CharField(max_length=128, blank=False, verbose_name=u'地址')
    account_bank = models.CharField(max_length=32, blank=True, verbose_name=u'汇款银行')
    account_no = models.CharField(max_length=32, blank=True, verbose_name=u'汇款帐号')

    memo = models.TextField(max_length=1024, blank=True, verbose_name=u'备注')

    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'修改日期')

    status = models.CharField(max_length=16, blank=True, choices=STATUS_CHOICES,
                              db_index=True, default=UNCHARGE, verbose_name=u'状态')

    progress = models.CharField(max_length=16, blank=True, choices=PROGRESS_CHOICES,
                                default=SELECTED, verbose_name=u'进度')
    supplier_type = models.IntegerField(choices=SUPPLIER_TYPE, blank=True, default=0, verbose_name=u"供应商类型")
    supplier_zone = models.IntegerField(default=0, db_index=True, verbose_name=u'供应商所属区域')
    buyer = models.ForeignKey(User, null=True, related_name='buyers', verbose_name=u'买手')
    ware_by = models.SmallIntegerField(default=WARE_SH, choices=WARE_CHOICES, verbose_name=u'所属仓库')

    objects = SaleSupplierManager()

    class Meta:
        db_table = 'supplychain_supply_supplier'
        app_label = 'supplier'
        verbose_name = u'特卖/供应商'
        verbose_name_plural = u'特卖/供应商列表'
        permissions = [
            ("sale_supplier_mgr", u"特卖供应商管理"),
        ]

    def __unicode__(self):
        return u'<%s,%s>' % (self.id, self.supplier_name)

    def is_active(self):
        """ 是否有效 """
        return self.status != self.FROZEN and self.progress not in (self.REJECTED, self.IGNORED)


class SupplierCharge(models.Model):
    """ 供应商接管信息表　"""
    EFFECT = 'effect'
    INVALID = 'invalid'
    STATUS_CHOICES = (
        (EFFECT, u'有效'),
        (INVALID, u'失效'),
    )

    supplier_id = models.IntegerField(default=0, verbose_name=u'供应商ID')
    employee = models.ForeignKey(User, related_name='employee_suppliers', verbose_name=u'接管人')

    status = models.CharField(max_length=16, blank=True, choices=STATUS_CHOICES,
                              default=EFFECT, verbose_name=u'状态')

    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'修改日期')

    class Meta:
        db_table = 'supplychain_supply_charge'
        unique_together = ("supplier_id", "employee")
        app_label = 'supplier'
        verbose_name = u'特卖/接管商家'
        verbose_name_plural = u'特卖/接管商家列表'

    def __unicode__(self):
        return '<{0},{1},{2}>'.format(self.supplier_id, self.employee, self.get_status_display())


class SupplierZone(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name=u'区域名称')

    class Meta:
        db_table = 'supplychain_supply_supplier_zone'
        app_label = 'supplier'
        verbose_name = u'特卖供应商区域表'
        verbose_name_plural = u'特卖供应商区域列表'

    def __unicode__(self):
        return "{0}".format(self.name)


class SaleProduct(models.Model):
    MANUAL = 'manual'
    MANUALINPUT = 'manualinput'
    TAOBAO = 'taobao'
    TMALL = 'tianmao'
    ZHEBABAI = 'zhe800'
    XIAOHER = 'xiaoher'
    VIP = 'vip'
    JHS = 'jhs'
    BBW = 'bbw'

    PLATFORM_CHOICE = (
        (MANUAL, u'手工录入'),
        (MANUALINPUT, u'线下店'),
        (TAOBAO, u'淘宝'),
        (TMALL, u'天猫'),
        (ZHEBABAI, u'折800'),
        (XIAOHER, u'小荷特卖'),
        (VIP, u'唯品会'),
        (JHS, u'聚划算'),
        (BBW, u'贝贝网'),)

    WAIT = 'wait'
    SELECTED = 'selected'
    PURCHASE = 'purchase'
    PASSED = 'passed'
    SCHEDULE = 'scheduling'
    IGNORED = 'ignored'
    REJECTED = 'rejected'
    STATUS_CHOICES = ((WAIT, u'待选'),
                      (SELECTED, u'入围'),
                      (PURCHASE, u'取样'),
                      (PASSED, u'通过'),
                      (SCHEDULE, u'排期'),
                      (REJECTED, u'淘汰'),
                      (IGNORED, u'忽略'),)

    outer_id = models.CharField(max_length=64, blank=True,
                                # default=lambda: 'OO%s' % int(time.time() * 10 ** 3),
                                verbose_name=u'外部ID')
    title = models.CharField(max_length=64, blank=True, db_index=True, verbose_name=u'标题')
    price = models.FloatField(default=0, verbose_name=u'价格')
    pic_url = models.CharField(max_length=512, blank=True, verbose_name=u'商品图片')
    product_link = models.CharField(max_length=512, blank=True, verbose_name=u'商品外部链接')

    sale_supplier = models.ForeignKey(SaleSupplier, null=True, related_name='supplier_products', verbose_name=u'供货商')
    sale_category = models.ForeignKey(SaleCategory, null=True, related_name='category_products', verbose_name=u'类别')
    platform = models.CharField(max_length=16, blank=True, default=MANUAL,
                                choices=PLATFORM_CHOICE, verbose_name=u'来自平台')

    hot_value = models.IntegerField(default=0, verbose_name=u'热度值')
    voting = models.BooleanField(default=False, verbose_name=u'参与投票')
    sale_price = models.FloatField(default=0, verbose_name=u'采购价')
    on_sale_price = models.FloatField(default=0, verbose_name=u'售价')
    std_sale_price = models.FloatField(default=0, verbose_name=u'吊牌价')
    product_material = models.CharField(max_length=16, blank=True, verbose_name=u'商品材质')
    memo = models.TextField(max_length=1024, blank=True, verbose_name=u'备注')
    is_changed = models.BooleanField(default=False, db_index=True, verbose_name=u'排期改动')

    status = models.CharField(max_length=16, blank=True,
                              choices=STATUS_CHOICES, default=WAIT, verbose_name=u'状态')

    contactor = models.ForeignKey(User, null=True, related_name='sale_products', verbose_name=u'接洽人')
    librarian = models.CharField(max_length=32, blank=True, null=True, verbose_name=u'资料员')
    buyer = models.CharField(max_length=32, blank=True, null=True, verbose_name=u'采购员')

    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'修改日期')
    sale_time = models.DateTimeField(null=True, blank=True, verbose_name=u'上架日期')
    reserve_time = models.DateTimeField(null=True, blank=True, verbose_name=u'预留时间')
    supplier_sku = models.CharField(max_length=64, blank=True, verbose_name=u'供应商货号')
    remain_num = models.IntegerField(default=0, verbose_name=u'预留数')

    class Meta:
        db_table = 'supplychain_supply_product'
        unique_together = ("outer_id", "platform")
        app_label = 'supplier'
        verbose_name = u'特卖/选品'
        verbose_name_plural = u'特卖/选品列表'
        permissions = [
            ("sale_product_mgr", u"特卖商品管理"),
            ("schedule_manage", u"排期管理")
        ]

    def __unicode__(self):
        return u'<%s,%s>' % (self.id, self.title)


from django.db.models.signals import pre_save, post_save
from common.modelutils import update_model_fields


def update_saleproduct_supplier(sender, instance, **kwargs):
    """
        如果选品录入，则更新供应商品最后选品日期,最后上架日期
    """
    if sender == SaleProduct:
        sale_supplier = instance.sale_supplier
        if (not sale_supplier or (sale_supplier.last_select_time and
                                          instance.created < sale_supplier.last_select_time)):
            return
        sale_supplier.last_select_time = instance.created
        update_model_fields(sale_supplier, update_fields=['last_select_time'])
    elif sender == SaleProductManageDetail:
        sale_products = SaleProduct.objects.filter(id=instance.sale_product_id)
        if not sale_products.exists():
            return
        sale_supplier = sale_products[0].sale_supplier
        sale_manage = instance.schedule_manage
        if (not sale_supplier or (sale_supplier.last_schedule_time and
                                          sale_manage.sale_time < sale_supplier.last_schedule_time.date())):
            return
        sale_supplier.last_schedule_time = sale_manage.sale_time
        update_model_fields(sale_supplier, update_fields=['last_schedule_time'])


post_save.connect(update_saleproduct_supplier, SaleProduct)


def change_saleprodut_by_pre_save(sender, instance, raw, *args, **kwargs):
    try:
        product = SaleProduct.objects.get(id=instance.id)
        # 如果上架时间修改，则重置is_verify
        if (product.status == SaleProduct.SCHEDULE and
                (product.sale_time != instance.sale_time or product.status != instance.status)):
            instance.is_changed = True
            update_model_fields(instance, update_fields=['is_changed'])
    except SaleProduct.DoesNotExist:
        pass


pre_save.connect(change_saleprodut_by_pre_save, sender=SaleProduct)


class SaleProductManage(models.Model):
    sale_time = models.DateField(db_index=True, unique=True, verbose_name=u'排期日期')
    product_num = models.IntegerField(default=0, verbose_name=u'商品数量')
    responsible_people_id = models.BigIntegerField(default=0, db_index=True, verbose_name=u'负责人ID')
    responsible_person_name = models.CharField(max_length=64, verbose_name=u'负责人名字')
    lock_status = models.BooleanField(default=False, verbose_name=u'锁定')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'修改日期')

    class Meta:
        db_table = 'supplychain_supply_schedule_manage'
        app_label = 'supplier'
        verbose_name = u'排期管理'
        verbose_name_plural = u'排期管理列表'

    @property
    def normal_detail(self):
        return self.manage_schedule.filter(today_use_status=SaleProductManageDetail.NORMAL)

    @property
    def nv_detail(self):
        return self.manage_schedule.filter(today_use_status=SaleProductManageDetail.NORMAL,
                                           sale_category__contains=u'女装')

    @property
    def child_detail(self):
        return self.manage_schedule.filter(today_use_status=SaleProductManageDetail.NORMAL,
                                           sale_category__contains=u'童装')

    def __unicode__(self):
        return '<%s,%s>' % (self.sale_time, self.responsible_person_name)


class SaleProductManageDetail(models.Model):
    COMPLETE = u'complete'
    WORKING = u'working'
    NORMAL = u'normal'
    DELETE = u'delete'
    use = u'working'
    TAKEOVER = u'takeover'
    NOTTAKEOVER = u'nottakeover'
    MATERIAL_STATUS = (
        (COMPLETE, u'全部完成'),
        (WORKING, u'进行中')
    )
    USE_STATUS = (
        (NORMAL, u'使用'),
        (DELETE, u'作废')
    )
    DESIGN_TAKE_STATUS = (
        (TAKEOVER, u'接管'),
        (NOTTAKEOVER, u'未接管')
    )
    schedule_manage = models.ForeignKey(SaleProductManage, related_name='manage_schedule', verbose_name=u'排期管理')
    sale_product_id = models.BigIntegerField(default=0, verbose_name=u"选品ID")
    name = models.CharField(max_length=64, verbose_name=u'选品名称')
    pic_path = models.CharField(max_length=512, blank=True, verbose_name=u'商品图片')
    sale_category = models.CharField(max_length=32, blank=True, verbose_name=u'商品分类')
    product_link = models.CharField(max_length=512, blank=True, verbose_name=u'商品外部链接')
    material_status = models.CharField(max_length=64, blank=True, default=WORKING, choices=MATERIAL_STATUS,
                                       verbose_name=u"资料状态")
    design_take_over = models.CharField(max_length=32, blank=True, default=NOTTAKEOVER, choices=DESIGN_TAKE_STATUS,
                                        verbose_name=u"平面资料接管状态")
    today_use_status = models.CharField(max_length=64, db_index=True, default=NORMAL, choices=USE_STATUS,
                                        verbose_name=u"使用状态")
    design_person = models.CharField(max_length=32, blank=True, verbose_name=u'设计负责人')
    design_complete = models.BooleanField(default=False, verbose_name=u'设计完成')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'修改日期')
    pic_rating = models.FloatField(blank=True, null=True, verbose_name=u'作图评分')
    is_approved = models.SmallIntegerField(default=0, verbose_name='审核通过')

    class Meta:
        db_table = 'supplychain_supply_schedule_manage_detail'
        app_label = 'supplier'
        verbose_name = u'排期管理明细'
        verbose_name_plural = u'排期管理明细列表'
        permissions = [
            ("revert_done", u"反完成"),
            ('pic_rating', u'作图评分'),
            ('add_product', u'加入库存商品'),
            ('eliminate_product', u'淘汰排期商品'),
            ('reset_head_img', u'重置头图')
        ]

    def __unicode__(self):
        return '<%s,%s>' % (self.id, self.sale_product_id)

    @property
    def sale_memo(self):
        try:
            sl_pro = SaleProduct.objects.get(id=self.sale_product_id)
            return sl_pro.memo
        except:
            return u""

    @property
    def std_purchase_price(self):
        try:
            sl_pro = SaleProduct.objects.get(id=self.sale_product_id)
            return sl_pro.sale_price
        except:
            return u"0.0"

    @property
    def pic_rating_memos(self):
        return self._pic_rating_memos.all().order_by('created')


post_save.connect(update_saleproduct_supplier, SaleProductManageDetail)


class SaleProductSku(models.Model):
    outer_id = models.CharField(max_length=64, blank=True, verbose_name=u'外部ID')

    product_color = models.CharField(max_length=64, blank=True, verbose_name=u'颜色')
    pic_url = models.CharField(max_length=512, blank=True, verbose_name=u'商品图片')
    properties_name = models.CharField(max_length=64, blank=True, db_index=True, verbose_name=u'规格')
    price = models.FloatField(default=0, verbose_name=u'价格')

    sale_product = models.ForeignKey(SaleProduct, null=True, related_name='product_skus', verbose_name=u'商品规格')
    sale_price = models.FloatField(default=0, verbose_name=u'采购价')
    spot_num = models.IntegerField(default=0, verbose_name=u'现货数量')
    memo = models.TextField(max_length=1024, blank=True, verbose_name=u'备注')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'修改日期')

    class Meta:
        db_table = 'supplychain_supply_productsku'
        unique_together = ("outer_id", "sale_product")
        app_label = 'supplier'
        verbose_name = u'特卖/选品规格'
        verbose_name_plural = u'特卖/选品规格列表'

    def __unicode__(self):
        return self.properties_name


class SaleProductPicRatingMemo(models.Model):
    schedule_detail = models.ForeignKey(SaleProductManageDetail, related_name='_pic_rating_memos',
                                        verbose_name=u'作图评分备注')
    memo = models.TextField(max_length=1024, blank=True, verbose_name=u'备注', default='[]')
    user = models.ForeignKey(User, related_name='pic_rating_admin', verbose_name=u'评分人')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')

    def __unicode__(self):
        return '%s: %s [%s]' % (self.user.username, self.memo, common.utils.get_timestr(self.created))

    class Meta:
        db_table = 'supplychain_supply_schedule_pic_rating_memo'
        app_label = 'supplier'
        verbose_name = u'排期作图评分'
        verbose_name_plural = u'排期作图评分'
