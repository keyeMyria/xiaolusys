#-*- coding:utf-8 -*-
"""
淘宝普通平台模型:
Product:系统内部商品，唯一对应多家店铺的商品外部编码,
ProductSku:淘宝平台商品sku，
Item:淘宝平台商品，
"""
import json
import datetime
from django.db import models
from django.db.models import Sum
from shopback.base.models import BaseModel,NORMAL,DELETE
from shopback.base.fields import BigIntegerAutoField
from shopback.categorys.models import Category,ProductCategory
from shopback.purchases.models import PurchaseProduct,PurchaseProductSku
from shopback.users.models import User
from auth import apis
import logging

logger  = logging.getLogger('items.handler')

ONSALE_STATUS  = 'onsale'
INSTOCK_STATUS = 'instock'

APPROVE_STATUS  = (
    (ONSALE_STATUS,'出售中'),
    (INSTOCK_STATUS,'库中'),
)


PRODUCT_STATUS = (
    (NORMAL,'使用'),
    (DELETE,'作废'),
)



class Product(models.Model):
    """ 抽象商品（根据淘宝外部编码)，描述：
        1,映射淘宝出售商品与采购商品桥梁；
        2,库存管理的核心类；
    """
    
    outer_id     = models.CharField(max_length=64,unique=True,null=False,blank=True,verbose_name='外部编码')
   
    name         = models.CharField(max_length=64,blank=True,verbose_name='商品名称')
    
    purchase_product = models.ForeignKey(PurchaseProduct,null=True,blank=True,related_name='products',verbose_name='关联采购商品')
    category     = models.ForeignKey(ProductCategory,null=True,blank=True,related_name='products',verbose_name='内部分类')
    
    pic_path = models.CharField(max_length=256,blank=True)
    
    collect_num  = models.IntegerField(verbose_name='库存数',default=0)  #库存数
    warn_num     = models.IntegerField(null=True,default=10,verbose_name='警告库位')    #警戒库位
    remain_num   = models.IntegerField(null=True,default=0,verbose_name='预留库位')    #预留库存
    price        = models.CharField(max_length=10,blank=True,verbose_name='参考价格')
    
    created      = models.DateTimeField(null=True,blank=True,auto_now_add=True,verbose_name='创建时间')
    modified     = models.DateTimeField(null=True,blank=True,auto_now=True,verbose_name='修改时间')
    
    sync_stock   = models.BooleanField(default=True,verbose_name='库存同步')
    out_stock    = models.BooleanField(default=False,verbose_name='缺货')
    is_assign    = models.BooleanField(default=False,verbose_name='取消库位警告') #是否手动分配库存，当库存充足时，系统自动设为False，手动分配过后，确定后置为True
    
    status       = models.CharField(max_length=16,db_index=True,choices=PRODUCT_STATUS,default=NORMAL,verbose_name='商品状态')
    
    class Meta:
        db_table = 'shop_items_product'
        verbose_name='库存商品'

    def __unicode__(self):
        return self.name
    
    @property
    def pskus(self):
        return self.prod_skus.filter(status=NORMAL)


class ProductSku(models.Model):
    """ 抽象商品规格（根据淘宝规格外部编码），描述：
        1,映射淘宝出售商品规格与采购商品规格桥梁；
        2,库存管理的规格核心类；
    """
    
    outer_id = models.CharField(max_length=64,null=True,blank=True,verbose_name='规格外部编码')
    
    prod_outer_id = models.CharField(max_length=64,db_index=True,blank=True,default='',verbose_name='商品外部编码')
    product  = models.ForeignKey(Product,null=True,related_name='prod_skus',verbose_name='商品')
    purchase_product_sku = models.ForeignKey(PurchaseProductSku,null=True,blank=True,related_name='prod_skus',verbose_name='关联采购规格')
    
    quantity = models.IntegerField(verbose_name='库存数',default=0)
    warn_num     = models.IntegerField(null=True,default=10,verbose_name='警戒库位')    #警戒库位
    remain_num   = models.IntegerField(null=True,default=0,verbose_name='预留库位')    #预留库存
    
    properties_name = models.TextField(max_length=200,blank=True,verbose_name='规格属性')
    properties      = models.TextField(max_length=200,blank=True,verbose_name='属性编码')
    
    out_stock    = models.BooleanField(default=False,verbose_name='缺货') 
    sync_stock   = models.BooleanField(default=True,verbose_name='库存同步') 
    is_assign    = models.BooleanField(default=False,verbose_name='已分配库存(取消库位警告)') #是否手动分配库存，当库存充足时，系统自动设为False，手动分配过后，确定后置为True
    
    modified = models.DateTimeField(null=True,blank=True,auto_now=True,verbose_name='修改时间')
    status   = models.CharField(max_length=10,db_index=True,choices=PRODUCT_STATUS,default=NORMAL,verbose_name='规格状态')  #normal,delete
    
    class Meta:
        db_table = 'shop_items_productsku'
        unique_together = ("outer_id", "product",)
        verbose_name='库存商品规格'

    def __unicode__(self):
        return self.properties_values
    
    def setQuantity(self,num):
        self.quantity = num
        self.save()
        
        total_nums = self.product.prod_skus.aggregate(total_nums=Sum('quantity')).get('total_nums')
        self.product.collect_num = total_nums or 0
        self.product.save()
    
    @property
    def properties_values(self):
        properties_list = self.properties_name.split(';')
        value_list = []
        for properties in properties_list:
            values = properties.split(':')
            value_list.append( '%s'%values[3] if len(values)==4 else properties)
        return ','.join(value_list)


class Item(models.Model):
    """ 淘宝线上商品 """
    
    num_iid  = models.CharField(primary_key=True,max_length=64,verbose_name='商品ID')

    user     = models.ForeignKey(User,null=True,related_name='items',verbose_name='店铺')
    category = models.ForeignKey(Category,null=True,related_name='items',verbose_name='淘宝分类')
    product  = models.ForeignKey(Product,null=True,related_name='items',verbose_name='关联库存商品')

    outer_id = models.CharField(max_length=64,blank=True,verbose_name='外部编码')
    num      = models.IntegerField(null=True,verbose_name='数量')

    seller_cids = models.CharField(max_length=126,blank=True,verbose_name='卖家分类')
    approve_status = models.CharField(max_length=20,choices=APPROVE_STATUS,blank=True,verbose_name='在售状态')  # onsale,instock
    type = models.CharField(max_length=12,blank=True,verbose_name='商品类型')
    valid_thru = models.IntegerField(null=True,verbose_name='有效期')

    price      = models.CharField(max_length=12,blank=True,verbose_name='价格')
    postage_id = models.BigIntegerField(null=True,verbose_name='运费模板ID')

    has_showcase = models.BooleanField(default=False,verbose_name='橱窗推荐')
    modified     = models.DateTimeField(null=True,blank=True,verbose_name='修改时间')

    list_time   = models.DateTimeField(null=True,blank=True,verbose_name='上架时间')
    delist_time = models.DateTimeField(null=True,blank=True,verbose_name='下架时间')

    has_discount = models.BooleanField(default=False,verbose_name='有折扣')

    props = models.TextField(max_length=500,blank=True,verbose_name='商品属性')
    title = models.CharField(max_length=148,blank=True,verbose_name='商品标题')
    property_alias = models.TextField(max_length=5000,blank=True,verbose_name='自定义属性')

    has_invoice = models.BooleanField(default=False,verbose_name='有发票')
    pic_url     = models.URLField(verify_exists=False,blank=True,verbose_name='商品图片')
    detail_url  = models.URLField(verify_exists=False,blank=True,verbose_name='详情链接')

    last_num_updated = models.DateTimeField(null=True,blank=True,verbose_name='最后库存同步日期')  #该件商品最后库存同步日期
    
    desc = models.TextField(max_length=25000,blank=True,verbose_name='商品描述')
    skus = models.TextField(max_length=5000,blank=True,verbose_name='规格')

    status = models.BooleanField(default=True,verbose_name='系统状态')
    class Meta:
        db_table = 'shop_items_item'
        verbose_name='线上商品'



    def __unicode__(self):
        return self.num_iid+'---'+self.outer_id+'---'+self.title
    
    @property
    def sku_list(self):
        try:
            return json.loads(self.skus)
        except:
            return {}
    
    @property
    def property_alias_dict(self):
	property_list = self.property_alias.split(';')
	property_dict = {}
	for p in property_list:
	    if p :
		r = p.split(':')
		property_dict['%s:%s'%(r[0],r[1])]=r[2]
	return property_dict


    @classmethod
    def get_or_create(cls,user_id,num_iid):
        item,state = Item.objects.get_or_create(num_iid=num_iid)
        if state:
            try:
                response  = apis.taobao_item_get(num_iid=num_iid,tb_user_id=user_id)
                item_dict = response['item_get_response']['item']
                item = Item.save_item_through_dict(user_id,item_dict)
            except Exception,exc:
                logger.error('商品更新出错(num_iid:%s)'%str(num_iid),exc_info=True)
        return item


    @classmethod
    def save_item_through_dict(cls,user_id,item_dict):
        
        category = Category.get_or_create(user_id,item_dict['cid'])
        if item_dict.has_key('outer_id'):
            product,state = Product.objects.get_or_create(outer_id=item_dict['outer_id'])
            if not product.name:
                product.collect_num = item_dict['num']
                product.price       = item_dict['price']
                product.name        = item_dict['title']
            product.pic_path    = item_dict['pic_url']    
            product.save()
    	else:
            logger.warn('item has no outer_id(num_iid:%s)'.decode('utf-8')%str(item_dict['num_iid']))
            product = None
        
        item,state    = cls.objects.get_or_create(num_iid = item_dict['num_iid'])
        
        for k,v in item_dict.iteritems():
            hasattr(item,k) and setattr(item,k,v)
        print item.outer_id,item.property_alias
        if not item.last_num_updated:
            item.last_num_updated = datetime.datetime.now()  
        
        item.user     = User.objects.get(visitor_id=user_id)
        item.product  = product
        item.category = category
        item.save()

        return item




