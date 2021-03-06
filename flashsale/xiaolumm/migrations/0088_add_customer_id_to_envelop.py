# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-18 16:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xiaolumm', '0087_exchangesaleorder_can_exchange'),
    ]

    operations = [
        migrations.AddField(
            model_name='envelop',
            name='customer_id',
            field=models.IntegerField(db_index=True, default=0, help_text='\u4e4b\u524d\u6570\u636e\u53ef\u80fd\u4e3a0, 2017.5.18\u6dfb\u52a0', verbose_name='\u63a5\u6536\u5ba2\u6237ID'),
        ),
        migrations.AlterField(
            model_name='envelop',
            name='platform',
            field=models.CharField(choices=[('wx_pub', '\u5fae\u4fe1\u516c\u4f17\u7ea2\u5305'), ('transfer', '\u5fae\u4fe1\u4f01\u4e1a\u8f6c\u8d26'), ('sandpay', '\u6749\u5fb7\u5b9e\u65f6\u4ee3\u4ed8')], db_index=True, max_length=8, verbose_name='\u7ea2\u5305\u53d1\u653e\u7c7b\u578b'),
        ),
        migrations.AlterField(
            model_name='envelop',
            name='recipient',
            field=models.CharField(db_index=True, max_length=28, verbose_name='\u63a5\u6536\u8005OPENID/\u94f6\u884c\u5361ID'),
        ),
        migrations.AlterField(
            model_name='envelop',
            name='send_status',
            field=models.CharField(choices=[('unsend', '\u5f85\u53d1\u653e'), ('sending', '\u53d1\u653e\u4e2d'), ('sent', '\u5df2\u53d1\u653e\u5f85\u9886\u53d6'), ('failed', '\u53d1\u653e\u5931\u8d25'), ('received', '\u5df2\u9886\u53d6'), ('refund', '\u5df2\u9000\u6b3e')], db_index=True, default='unsend', max_length=8, verbose_name='\u6e20\u9053\u53d1\u9001\u72b6\u6001'),
        ),
    ]
