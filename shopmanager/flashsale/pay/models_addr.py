#-*- coding:utf-8 -*-
from django.db import models
from django.db.models.signals import  post_save

from .base import PayBaseModel,BaseModel
from . import managers


class District(PayBaseModel):
    
    FIRST_STAGE  = 1
    SECOND_STAGE = 2
    THIRD_STAGE  = 3
    FOURTH_STAGE = 4
    
    STAGE_CHOICES = ((FIRST_STAGE,u'1'),
                     (SECOND_STAGE,u'2'),
                     (THIRD_STAGE,u'3'),
                     (FOURTH_STAGE,u'4'),)
    
    id     = models.AutoField(primary_key=True,verbose_name=u'ID')
    parent_id = models.IntegerField(null=False,default=0,db_index=True,verbose_name=u'父ID')
    name    = models.CharField(max_length=32,blank=True,verbose_name=u'地址名')
    
    grade   = models.IntegerField(default=0,choices=STAGE_CHOICES,verbose_name=u'等级')
    sort_order = models.IntegerField(default=0,verbose_name=u'优先级')
    
    class Meta:
        db_table = 'flashsale_district' 
        verbose_name = u'省市/区划'
        verbose_name_plural = u'省市/区划列表'
        
    def __unicode__(self):
        return '%s,%s'%(self.id,self.name)
    
    @property
    def full_name(self):
        
        if self.parent_id and self.parent_id != 0:

            try:
                dist = self.__class__.objects.get(id=self.parent_id)
            except:
                return '[父ID未找到]-%s'%self.name
            else:
                return '%s,%s'%(dist.full_name,self.name)
        return self.name
    
    
class UserAddress(BaseModel):
    
    NORMAL = 'normal'
    DELETE = 'delete'
    
    STATUS_CHOICES = ((NORMAL,u'正常'),
                      (DELETE,u'删除'))
    
    cus_uid          =  models.BigIntegerField(db_index=True,verbose_name=u'客户ID')
    
    receiver_name    =  models.CharField(max_length=25,
                                         blank=True,verbose_name=u'收货人姓名')
    receiver_state   =  models.CharField(max_length=16,blank=True,verbose_name=u'省')
    receiver_city    =  models.CharField(max_length=16,blank=True,verbose_name=u'市')
    receiver_district  =  models.CharField(max_length=16,blank=True,verbose_name=u'区')
    
    receiver_address   =  models.CharField(max_length=128,blank=True,verbose_name=u'详细地址')
    receiver_zip       =  models.CharField(max_length=10,blank=True,verbose_name=u'邮编')
    receiver_mobile    =  models.CharField(max_length=11,db_index=True,blank=True,verbose_name=u'手机')
    receiver_phone     =  models.CharField(max_length=20,blank=True,verbose_name=u'电话')
    
    default         = models.BooleanField(default=False,verbose_name=u'默认地址')
    
    status          = models.CharField(max_length=8,blank=True,db_index=True,default=NORMAL,
                                       choices=STATUS_CHOICES,verbose_name=u'状态')

    objects = models.Manager()
    normal_objects = managers.NormalUserAddressManager()
    class Meta:
        #db_table = 'flashsale_address'
        db_table = 'flashsale_address'
        verbose_name = u'特卖用户/地址'
        verbose_name_plural = u'特卖用户/地址列表'
        
    def __unicode__(self):
        
        return '<%s,%s>'%(self.id,self.cus_uid)

    def set_default_address(self):
        """ 设置默认地址 """
        current_address = self.__class__.objects.filter(cus_uid=self.cus_uid)  # 当前用户的地址
        current_address.update(default=False)  # 全部更新为非默认
        self.default = True
        self.save()  # 保存当前的为默认地址
        return True

    def clean_strip(self):
        changed = False
        for attr in ['receiver_name', 'receiver_phone', 'receiver_state', 'receiver_city', 'receiver_district', 'receiver_address']:
            val = getattr(self, attr)
            if val.strip() != val:
                changed = True
                setattr(self, attr, val.strip())
        return changed