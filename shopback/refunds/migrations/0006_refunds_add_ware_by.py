# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-22 10:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('refunds', '0005_refundproduct_in_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='refund',
            name='ware_by',
            field=models.IntegerField(choices=[(0, '\u672a\u9009\u4ed3'), (1, '\u4e0a\u6d77\u4ed3'), (2, '\u5e7f\u5dde\u4ed3'), (4, '\u8702\u5de2\u82cf\u5dde\u4ed3'), (5, '\u8702\u5de2\u5e7f\u5dde\u4ed3'), (3, '\u516c\u53f8\u4ed3'), (9, '\u7b2c\u4e09\u65b9\u4ed3')], default=None, null=True, verbose_name='\u9000\u8d27\u4ed3\u5e93'),
        ),
        migrations.AlterField(
            model_name='refund',
            name='status',
            field=models.CharField(blank=True, choices=[(b'NO_REFUND', '\u6ca1\u6709\u9000\u6b3e'), (b'WAIT_SELLER_AGREE', '\u4e70\u5bb6\u5df2\u7ecf\u7533\u8bf7\u9000\u6b3e'), (b'WAIT_BUYER_RETURN_GOODS', '\u5356\u5bb6\u5df2\u7ecf\u540c\u610f\u9000\u6b3e'), (b'WAIT_SELLER_CONFIRM_GOODS', '\u4e70\u5bb6\u5df2\u7ecf\u9000\u8d27'), (b'SELLER_REFUSE_BUYER', '\u5356\u5bb6\u62d2\u7edd\u9000\u6b3e'), (b'CLOSED', '\u9000\u6b3e\u5173\u95ed'), (b'SUCCESS', '\u9000\u6b3e\u6210\u529f')], max_length=32, verbose_name='\u9000\u8d27\u72b6\u6001'),
        ),
    ]
