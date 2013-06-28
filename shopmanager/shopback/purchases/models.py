#-*- coding:utf8 -*-
from django.db import models
from django.db.models.signals import post_save
from django.db.models import Q,Sum
from shopback import paramconfig as pcfg
from shopback.archives.models import Supplier,PurchaseType,Deposite
from shopback.categorys.models import ProductCategory
from shopback.items.models import Product,ProductSku
from auth.utils import format_date
from utils import update_model_feilds

PURCHASE_STATUS = (
    (pcfg.PURCHASE_DRAFT,'草稿'),
    (pcfg.PURCHASE_APPROVAL,'审批'),
    (pcfg.PURCHASE_FINISH,'完成'),
    (pcfg.PURCHASE_INVALID,'作废'),
)

PURCHASE_ITEM_STATUS = (
    (pcfg.PURCHASE_DRAFT,'草稿'),
    (pcfg.PURCHASE_APPROVAL,'审批'),
    (pcfg.PURCHASE_RETURN,'退货'),
    (pcfg.PURCHASE_CLOSE,'退货关闭'),
    (pcfg.PURCHASE_FINISH,'完成'),
    (pcfg.PURCHASE_INVALID,'作废'),
    (pcfg.PURCHASE_REWORD,'返修'),
    (pcfg.PURCHASE_REWORDOVER,'返修结束'),
)

PURCHASE_STORAGE_STATUS = (
    (pcfg.PURCHASE_DRAFT,'草稿'),
    (pcfg.PURCHASE_APPROVAL,'已审批')
)

PURCHASE_PAYMENT_TYPE = (
    (pcfg.PC_COD_TYPE,'货到付款'),
    (pcfg.PC_PREPAID_TYPE,'预付款'),
    (pcfg.PC_POD_TYPE,'付款提货'),
    (pcfg.PC_OTHER_TYPE,'其它'),
)

PRODUCT_STATUS = (
    (pcfg.NORMAL,'使用'),
    (pcfg.DELETE,'作废'),
)


class Purchase(models.Model):
    """ 采购合同 """
    
    supplier     = models.ForeignKey(Supplier,null=True,blank=True,related_name='purchases',verbose_name='供应商')
    deposite     = models.ForeignKey(Deposite,null=True,blank=True,related_name='purchases',verbose_name='仓库')
    purchase_type = models.ForeignKey(PurchaseType,null=True,blank=True,related_name='purchases',verbose_name='采购类型')
    
    forecast_date = models.DateField(null=True,blank=True,verbose_name='预测到货日期')
    post_date     = models.DateField(null=True,blank=True,verbose_name='发货日期')
    service_date  = models.DateField(null=True,blank=True,verbose_name='业务日期')
    
    created      = models.DateTimeField(null=True,blank=True,auto_now=True,verbose_name='创建日期')
    modified     = models.DateTimeField(null=True,blank=True,auto_now_add=True,verbose_name='修改日期')
    
    total_fee    = models.FloatField(default=0.0,verbose_name='总费用')
    payment      = models.FloatField(default=0.0,verbose_name='实付')
    
    status       = models.CharField(max_length=32,db_index=True,choices=PURCHASE_STATUS,
                                    default=pcfg.PURCHASE_DRAFT,verbose_name='采购状态')
    
    extra_name   = models.CharField(max_length=256,blank=True,verbose_name='标题')
    extra_info   = models.TextField(blank=True,verbose_name='备注')
    
    #attach_files 关联文件
    class Meta:
        db_table = 'shop_purchases_purchase'
        verbose_name=u'采购单'

    def __unicode__(self):
        return '<%s,%s>'%(str(self.id),self.extra_name)
    
    def gen_csv_tuple(self):
        
        pcsv = []
        pcsv.append((u'采购编号',str(self.id),u'采购标题',self.extra_name,u'供应商',self.supplier.supplier_name))
        pcsv.append((u'采购日期',format_date(self.service_date),u'预测到货日期',format_date(self.forecast_date)))
        pcsv.append((u'总费用',str(self.total_fee),u'实付',str(self.payment)))
        pcsv.append(('',''))
        
        pcsv.append((u'商品编码',u'商品名称',u'规格编码',u'规格名称',u'采购价',u'采购数量'))
        for item in self.purchase_items.exclude(status__in=(pcfg.PURCHASE_CLOSE,pcfg.PURCHASE_INVALID)).order_by('product'):
            pcsv.append((item.product.outer_id,
                         item.product.name,
                         item.product_sku.outer_id,
                         item.product_sku.properties_alias or item.product_sku.properties_name,
                         str(item.price),
                         str(item.purchase_num)))
            
        return pcsv  
    
class PurchaseItem(models.Model):
    """ 采购项目 """
    
    purchase     = models.ForeignKey(Purchase,related_name='purchase_items',verbose_name='采购单')
    supplier_item_id = models.CharField(max_length=64,blank=True,verbose_name='供应商产品编码')
    
    product      = models.ForeignKey(Product,related_name='purchase_items',verbose_name='采购产品')
    product_sku  = models.ForeignKey(ProductSku,related_name='purchase_items',verbose_name='采购产品规格')
    
    purchase_num = models.IntegerField(null=True,verbose_name='采购数量')
    discount     = models.FloatField(null=True,verbose_name='折扣')
    
    price        = models.FloatField(null=True,verbose_name='进价')

    total_fee    = models.FloatField(null=True,verbose_name='总费用')
    payment      = models.FloatField(null=True,verbose_name='实付')
    
    created      = models.DateTimeField(null=True,blank=True,auto_now=True,verbose_name='创建日期')
    modified     = models.DateTimeField(null=True,blank=True,auto_now_add=True,verbose_name='修改日期')
    
    status       = models.CharField(max_length=32,db_index=True,choices=PURCHASE_ITEM_STATUS,
                                    default=pcfg.PURCHASE_DRAFT,verbose_name='状态')
    
    extra_info   = models.TextField(blank=True,verbose_name='备注')
    
    class Meta:
        db_table = 'shop_purchases_item'
        verbose_name='采购项目'
    
    def __unicode__(self):
        return 'CGZD%d'%self.id
 
 
def update_purchase_info(sender,instance,*args,**kwargs):
    """ 更新采购单信息 """
    
    instance.total_fee = int(instance.purchase_num or 0)*float(instance.price or 0)
    update_model_feilds(instance,update_fields=['total_fee'])
    
    purchase = instance.purchase
    purchase_items = instance.purchase.purchase_items
    purchase.total_fee = purchase_items.aggregate(total_fees=Sum('total_fee'))['total_fees'] or 0
    purchase.payment   = purchase_items.aggregate(total_payment=Sum('payment'))['total_payment'] or 0
    
    update_model_feilds(purchase,update_fields=['total_fee','payment'])
        
post_save.connect(update_purchase_info, sender=PurchaseItem)
    
    
class PurchaseStorage(models.Model):
    """ 采购入库单 """
    
    supplier     = models.ForeignKey(Supplier,null=True,blank=True,related_name='purchase_storages',verbose_name='供应商')
    deposite     = models.ForeignKey(Deposite,null=True,blank=True,related_name='purchases_storages',verbose_name='仓库')
    purchase_type = models.ForeignKey(PurchaseType,null=True,blank=True,related_name='purchases_storages',verbose_name='采购类型')
    
    forecast_date = models.DateTimeField(null=True,blank=True,verbose_name='预计到货日期')
    post_date     = models.DateTimeField(null=True,blank=True,verbose_name='实际到货日期')

    created      = models.DateTimeField(null=True,blank=True,auto_now=True,verbose_name='创建日期')
    modified     = models.DateTimeField(null=True,blank=True,auto_now_add=True,verbose_name='修改日期')
    
    status       = models.CharField(max_length=32,db_index=True,choices=PURCHASE_STORAGE_STATUS,
                                    default=pcfg.PURCHASE_DRAFT,verbose_name='状态')
    
    extra_name  = models.CharField(max_length=256,blank=True,verbose_name='标题')
    extra_info  = models.TextField(blank=True,verbose_name='备注')
    
    class Meta:
        db_table = 'shop_purchases_storage'
        verbose_name='采购入库单'

    def __unicode__(self):
        return 'RKD%d'%self.id
     

class PurchaseStorageItem(models.Model):
    """ 采购入库项目 """
    
    purchase_storage     = models.ForeignKey(PurchaseStorage,related_name='purchase_storage_items',verbose_name='关联入库单')
    supplier_item_id     = models.CharField(max_length=64,blank=True,verbose_name='供应商商品编号')
    
    product      = models.ForeignKey(Product,related_name='purchase_storage_items',verbose_name='采购商品')
    product_sku  = models.ForeignKey(ProductSku,related_name='purchase_storage_items',verbose_name='采购商品规格')
    
    storage_num  = models.IntegerField(null=True,verbose_name='入库数量')

    created      = models.DateTimeField(null=True,blank=True,auto_now=True,verbose_name='创建日期')
    modified     = models.DateTimeField(null=True,blank=True,auto_now_add=True,verbose_name='修改日期')
    
    status       = models.CharField(max_length=32,db_index=True,choices=PURCHASE_STORAGE_STATUS,
                                    default=pcfg.PURCHASE_DRAFT,verbose_name='入库状态')
    
    extra_info   = models.TextField(blank=True,verbose_name='备注')
    
    class Meta:
        db_table = 'shop_purchases_storageitem'
        verbose_name = '采购入库项目'
    
    def __unicode__(self):
        return 'RKZD%d'%self.id
    
    
class PurchaseStorageRelate(models.Model):
    """ 采购入库项目关联 """
    
    purchase_item = models.ForeignKey(PurchaseItem,related_name='purchase_relates',verbose_name='采购项目')
    
    storage_item  = models.ForeignKey(PurchaseStorageItem,related_name='purchase_relates',verbose_name='入库项目')
    
    relate_num    = models.IntegerField(null=True,verbose_name='入库数量')
    class Meta:
        db_table = 'shop_purchases_storage_relate'
        verbose_name='采购入库项目关联'
    
    def __unicode__(self):
        return '<%s,%s,%d>'%(self.purchase_item.purchase,self.storage_item.purchase_storage,self.relate_num)
    

class PurchasePaymentItem(models.Model):
    """ 
        采购付款项目：
        1,货到付款
        2,预付款
        3,付款提货
    """    
    
    purchase  = models.ForeignKey(Purchase,null=True,related_name='purchase_payment',verbose_name='采购合同')
    
    storage   = models.ForeignKey(PurchaseStorage,null=True,related_name='purchase_payment',verbose_name='入库单')
    
    pay_type  = models.CharField(max_length=4,db_index=True,choices=PURCHASE_PAYMENT_TYPE,verbose_name='付款类型')
    
    pay_time     = models.DateTimeField(null=True,blank=True,verbose_name='付款日期')
    
    payment   = models.FloatField(default=0,verbose_name='付款金额')
    
    status       = models.CharField(max_length=32,db_index=True,verbose_name='状态')
    
    extra_info   = models.TextField(max_length=1000,blank=True,verbose_name='备注')
    
    class Meta:
        db_table = 'shop_purchases_payment_item'
        verbose_name='采购付款项目'
    
    def __unicode__(self):
        return '<%s,%s,%s>'%(str(self.purchase),str(self.storage),str(self.payment))
    
    