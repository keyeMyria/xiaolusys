#-*- coding:utf-8 -*-
import datetime
import urllib,urllib2
from django.conf import settings
from django.db import models
import pingpp


class Envelop(models.Model):
    
    WXPUB  = 'wx_pub'
    ENVELOP_CHOICES = ((WXPUB,u'微信公众'),)
    
    WAIT_SEND = 'wait'
    CONFIRM_SEND = 'confirm'
    CANCEL    = 'cancel'
    FAIL      = 'fail'
    
    STATUS_CHOICES = ((WAIT_SEND,u'待发送'),
                      (CONFIRM_SEND,u'已发送'),
                      (FAIL,u'发送失败'),
                      (CANCEL,u'已取消'),)
    
    CASHOUT = 'cashout'
    SUBJECT_CHOICES = ((CASHOUT,u'钱包提现'),)
    
    envelop_id   = models.CharField(max_length=28,blank=True,db_index=True,verbose_name=u'红包ID')
    
    amount       = models.IntegerField(default=0,verbose_name=u'红包金额')
    
    platform     = models.CharField(max_length=8,db_index=True,choices=ENVELOP_CHOICES,verbose_name=u'来自平台')
    livemode     = models.BooleanField(default=True,verbose_name=u'是否有效')
    
    recipient    = models.CharField(max_length=28,db_index=True,verbose_name=u'接收者OPENID')
    receiver     = models.CharField(max_length=64,blank=True,db_index=True,verbose_name=u'小鹿妈妈编号')
    
    subject      = models.CharField(max_length=8,db_index=True,choices=SUBJECT_CHOICES,verbose_name=u'红包主题')
    body         = models.CharField(max_length=128,blank=True,verbose_name=u'红包祝福语')
    description  = models.CharField(max_length=255,blank=True,verbose_name=u'备注信息')
    
    status       = models.CharField(max_length=8,db_index=True,default=WAIT_SEND,
                                    choices=STATUS_CHOICES,verbose_name=u'状态')
    
    referal_id   = models.CharField(max_length=32,blank=True,db_index=True,verbose_name=u'引用ID')
    send_time    = models.DateTimeField(db_index=True,blank=True,null=True,verbose_name=u'发送时间')
    created      = models.DateTimeField(auto_now_add=True,verbose_name=u'创建日期')
    modified     = models.DateTimeField(auto_now=True,verbose_name=u'修改日期')

    class Meta:
        db_table = 'flashsale_envelop'
        app_label = 'xiaolumm'
        verbose_name=u'微信/红包'
        verbose_name_plural = u'微信/红包列表'
    
    def __unicode__(self):
        return '%s'%(self.id)
    
    @property
    def amount_cash(self):
        return self.amount / 100.0
    
    def get_amount_display(self):
        return self.amount_cash
    
    get_amount_display.allow_tags = True
    get_amount_display.admin_order_field = 'amount'
    get_amount_display.short_description = u"红包金额"
    
    
    def send_envelop(self):
        pingpp.api_key = settings.PINGPP_APPKEY
        try:
            if self.envelop_id:
                redenvelope = pingpp.RedEnvelope.retrieve(self.envelop_id)
            else:
                redenvelope = pingpp.RedEnvelope.create(
                        order_no=str(self.id),
                        channel=self.platform,
                        amount=self.amount,
                        subject=self.get_subject_display(),
                        body=self.body,
                        currency='cny',
                        app=dict(id=settings.PINGPP_APPID),
                        extra=dict(nick_name=u'上海己美网络科技',send_name=u'小鹿美美'),
                        recipient=self.recipient,
                        description=self.description
                    )
        except Exception,exc:
            self.status = Envelop.FAIL
            self.save()
            raise exc
        else:
            is_paid = redenvelope['paid']
            self.envelop_id = redenvelope['id']
            self.livemode   = redenvelope['livemode']
            if is_paid:
                self.send_time  = datetime.datetime.now()
                self.status     = Envelop.CONFIRM_SEND 
                self.save()
            else:
                self.status     = Envelop.FAIL
                self.save()
                raise Exception(u'红包付款失败！')
    
    
    
    
    