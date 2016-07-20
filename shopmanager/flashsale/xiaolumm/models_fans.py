# coding=utf-8

from django.db import models
from django.db.models.signals import post_save
from core.models import BaseModel
from .managers import XlmmFansManager
from flashsale.pay.models import Customer


class XlmmFans(BaseModel):
    xlmm = models.BigIntegerField(verbose_name='小鹿妈妈id')
    xlmm_cusid = models.BigIntegerField(db_index=True, verbose_name='小鹿妈妈用户id')
    refreal_cusid = models.BigIntegerField(db_index=True, verbose_name='推荐人用户id')
    fans_cusid = models.BigIntegerField(unique=True, verbose_name='粉丝用户id')
    fans_nick = models.CharField(max_length=32, blank=True, null=True, verbose_name='粉丝昵称')
    fans_thumbnail = models.CharField(max_length=256, blank=True, null=True, verbose_name='粉丝头像')
    objects = XlmmFansManager()

    class Meta:
        unique_together = ('xlmm', 'fans_cusid')
        db_table = 'flashsale_xlmm_fans'
        app_label = 'xiaolumm'
        verbose_name = u'代理/粉丝表'
        verbose_name_plural = u'代理/粉丝列表'

    def __unicode__(self):
        return "<%s,%s>" % (self.xlmm, self.fans_cusid)

    def getCustomer(self):
        """ 获取粉丝在特卖客户列表中的信息 """
        if not hasattr(self, '_fans_customer_'):
            self._fans_customer_ = Customer.objects.normal_customer.filter(id=self.fans_cusid).first()
        return self._fans_customer_

    def fans_description(self):
        if self.xlmm_cusid == self.refreal_cusid:
            return u"通过您的分享成为粉丝"
        return u"来自好友的分享"

    def nick_display(self):
        if not self.fans_nick:
            return u"匿名用户"
        return self.fans_nick


def update_activevalue(sender, instance, created, **kwargs):
    """
    更新妈妈活跃度
    """
    if not created:
        return

    from flashsale.xiaolumm import tasks_mama_activevalue
    mama_id = instance.xlmm
    fans_customer_id = instance.fans_cusid
    date_field = instance.created.date()
    tasks_mama_activevalue.task_fans_update_activevalue.delay(mama_id, fans_customer_id, date_field)


post_save.connect(update_activevalue, sender=XlmmFans, dispatch_uid='post_save_update_activevalue')


def update_mamafortune_fans_num(sender, instance, created, **kwargs):
    if not created:
        return
    from flashsale.xiaolumm import tasks_mama_fortune
    mama_id = instance.xlmm
    tasks_mama_fortune.task_update_mamafortune_fans_num.delay(mama_id)


post_save.connect(update_mamafortune_fans_num,
                  sender=XlmmFans, dispatch_uid='post_save_update_mamafortune_fans_num')


class FansNumberRecord(BaseModel):
    xlmm = models.BigIntegerField(db_index=True, verbose_name='小鹿妈妈id')
    xlmm_cusid = models.BigIntegerField(db_index=True, verbose_name='小鹿妈妈用户id')
    fans_num = models.IntegerField(default=1, verbose_name='粉丝数量')

    class Meta:
        unique_together = ('xlmm', 'xlmm_cusid')
        db_table = 'flashsale_xlmm_fans_nums'
        app_label = 'xiaolumm'
        verbose_name = u'代理/粉丝数量表'
        verbose_name_plural = u'代理/粉丝数量列表'

    def __unicode__(self):
        return "<%s,%s>" % (self.xlmm, self.fans_num)


def login_activate_appdownloadrecord(user):
    """
    Only check whether this user has download-relationship, if he/she has
    and that download-relationship record is not used yet, we confirm he/she is 
    a fan of the related user.
    """

    from flashsale.xiaolumm.tasks_mama_relationship_visitor import task_login_activate_appdownloadrecord, task_login_create_appdownloadrecord
    task_login_activate_appdownloadrecord.delay(user)
    #task_login_create_appdownloadrecord.delay()


