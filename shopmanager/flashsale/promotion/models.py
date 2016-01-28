#-*- coding:utf8 -*-
import datetime
from django.db import models
from core.models import BaseModel
from django.contrib.auth.models import User
from shopback.base.models import JSONCharMyField
from .models_freesample import XLFreeSample, XLSampleApply, XLSampleOrder, XLSampleSku

SAFE_CODE_SECONDS = 180
TOKEN_EXPIRED_IN  = 15 * 60


class XLInviteCode(BaseModel):
    """ 用户活动邀请码 """
    CODE_TYPES = ((0,u'免费试用'), (1,u'招募代理'))
    
    mobile    = models.CharField(max_length=11, unique=True, verbose_name=u'手机号码')
    
    vipcode   = models.CharField(max_length=16,unique=True,null=False,
                                 blank=False,verbose_name=u'邀请码')
    expiried  = models.DateTimeField(null=False,blank=False,verbose_name=u'过期时间')
    
    ### 1. for getting samples; 2. for purchase discount
    code_type = models.IntegerField(default=0, choices=CODE_TYPES, verbose_name=u'邀请码类型')
    
    ### get $10 for $50 purchase; get $25 for $100 purchase;
    code_rule = models.CharField(max_length=256,null=False,blank=True,verbose_name=u'使用规则')
    
    ### once or multiple times
    max_usage = models.IntegerField(default=0,verbose_name=u'可用次数')
    usage_count = models.IntegerField(default=0,db_index=True,verbose_name=u'已使用')
    
    class Meta:
        db_table = 'flashsale_promotion_invitecode'
        verbose_name = u'推广/活动邀请码'
        verbose_name_plural = u'推广/活动邀请码列表'
        
        
class XLReferalRelationship(BaseModel):
    """ 用户邀请引用关系 """
    
    referal_uid = models.CharField(max_length=64,unique=True,verbose_name=u"被推荐人ID")
    referal_from_uid = models.CharField(max_length=64,db_index=True,verbose_name=u"推荐人ID")
    
    class Meta:
        db_table = 'flashsale_promotion_relationship'
        verbose_name = u'推广/用户邀请关系'
        verbose_name_plural = u'推广/用户邀请关系'
    
