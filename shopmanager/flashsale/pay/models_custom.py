#-*- coding:utf-8 -*-
from django.db import models
from shopback.items.models import Product

class Productdetail(models.Model):
    
    OUT_PERCENT = 0 #未设置代理返利比例
    ZERO_PERCENT = -1
    TEN_PERCENT = 10
    TWENTY_PERCENT = 20
    THIRTY_PERCENT = 30

    REBETA_CHOICES = ((OUT_PERCENT,u'未设置返利'),
                     (ZERO_PERCENT,u'该商品不返利'),
                     (TEN_PERCENT,u'返利百分之10'),
                     (TWENTY_PERCENT,u'返利百分之20'),
                     (THIRTY_PERCENT,u'返利百分之30'),)
    
    product  = models.OneToOneField(Product, primary_key=True,related_name='details',verbose_name=u'库存商品')
    
    head_imgs  = models.TextField(blank=True,verbose_name=u'题头照(多张请换行)')
    
    content_imgs = models.TextField(blank=True,verbose_name=u'内容照(多张请换行)')
    
    mama_discount  = models.IntegerField(default=100,verbose_name=u'妈妈折扣')
    
    is_recommend = models.BooleanField(db_index=True,verbose_name=u'专区推荐')
    
    buy_limit    = models.BooleanField(default=False,verbose_name=u'是否限购')
    per_limit    = models.IntegerField(default=5,verbose_name=u'限购数量')
    
    mama_rebeta  = models.IntegerField(default=OUT_PERCENT, choices=REBETA_CHOICES, 
					db_index=True, verbose_name=u'代理返利')

    class Meta:
        db_table = 'flashsale_productdetail'
        verbose_name=u'特卖商品/详情'
        verbose_name_plural = u'特卖商品/详情列表'
    
    def __unicode__(self):
        return '<%s,%s>'%(self.product.outer_id,self.product.name)
    
    def mama_rebeta_rate(self):
        if self.mama_rebeta == self.ZERO_PERCENT:
            return 0.0
        if self.mama_rebeta == self.OUT_PERCENT:
            return None
        rate = self.mama_rebeta / 100.0
        assert rate >= 0 and rate <=1
        return rate 
    
    
class ModelProduct(models.Model):
    
    NORMAL = '0'
    DELETE = '1'
    
    STATUS_CHOICES = ((NORMAL,u'正常'),
                      (DELETE,u'作废'))
    
    name       = models.CharField(max_length=64,db_index=True,verbose_name=u'款式名称')
    
    head_imgs  = models.TextField(blank=True,verbose_name=u'题头照(多张请换行)')
    
    content_imgs = models.TextField(blank=True,verbose_name=u'内容照(多张请换行)')
    
    buy_limit    = models.BooleanField(default=False,verbose_name=u'是否限购')
    per_limit    = models.IntegerField(default=5,verbose_name=u'限购数量')
    
    sale_time    = models.DateField(null=True,blank=True,db_index=True,verbose_name=u'上架日期')
    
    created      = models.DateTimeField(auto_now_add=True,verbose_name=u'创建时间')
    modified     = models.DateTimeField(auto_now=True,verbose_name=u'修改时间')
    
    status       = models.CharField(max_length=16,db_index=True,
                                    choices=STATUS_CHOICES,
                                    default=NORMAL,verbose_name=u'状态')
    
    class Meta:
        db_table = 'flashsale_modelproduct'
        unique_together = ("id", "name")
        verbose_name=u'特卖商品/款式'
        verbose_name_plural = u'特卖商品/款式列表'
     
    def __unicode__(self):
        return '<%s,%s>'%(self.id,self.name)
    
from shopback.base.models import JSONCharMyField

POSTER_DEFAULT =(
'''
[
  {
    "subject":["2折起","Joan&David  女装专场"],
    "item_link":"商品链接",
    "pic_link":"海报图片"
  }
]
''')

class GoodShelf(models.Model):
    
    title = models.CharField(max_length=32,db_index=True,blank=True, verbose_name=u'海报说明')
    
    wem_posters   = JSONCharMyField(max_length=10240, blank=True, 
                                    default=POSTER_DEFAULT, 
                                    verbose_name=u'女装海报')
    chd_posters   = JSONCharMyField(max_length=10240, blank=True, 
                                    default=POSTER_DEFAULT,
                                    verbose_name=u'童装海报')
    
    is_active    = models.BooleanField(default=True,verbose_name=u'上线')
    active_time  = models.DateTimeField(db_index=True,null=True,blank=True,verbose_name=u'上线日期')
    
    created      = models.DateTimeField(null=True,auto_now_add=True,db_index=True,blank=True,verbose_name=u'生成日期')
    modified     = models.DateTimeField(null=True,auto_now=True,blank=True,verbose_name=u'修改日期')
    
    class Meta:
        db_table = 'flashsale_goodshelf'
        verbose_name=u'特卖商品/海报'
        verbose_name_plural = u'特卖商品/海报列表'
    
    def __unicode__(self):
        return u'<海报：%s>'%(self.title)
    
    
