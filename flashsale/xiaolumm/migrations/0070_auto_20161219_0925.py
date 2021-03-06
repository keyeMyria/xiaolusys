# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-19 09:25
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xiaolumm', '0069_auto_20161203_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrylog',
            name='carry_date',
            field=models.DateField(db_index=True, default=datetime.date.today, verbose_name='\u4e1a\u52a1\u65e5\u671f'),
        ),
        migrations.AlterField(
            model_name='carrylog',
            name='carry_type',
            field=models.CharField(blank=True, choices=[('out', '\u652f\u51fa'), ('in', '\u6536\u5165')], db_index=True, default='out', max_length=8, verbose_name='\u76c8\u8d1f'),
        ),
        migrations.AlterField(
            model_name='carrylog',
            name='log_type',
            field=models.CharField(blank=True, choices=[('rebeta', '\u8ba2\u5355\u8fd4\u5229'), ('buy', '\u6d88\u8d39\u652f\u51fa'), ('refund', '\u9000\u6b3e\u8fd4\u73b0'), ('reoff', '\u9000\u6b3e\u6263\u9664'), ('click', '\u70b9\u51fb\u5151\u73b0'), ('cashout', '\u94b1\u5305\u63d0\u73b0'), ('deposit', '\u62bc\u91d1'), ('thousand', '\u5343\u5143\u63d0\u6210'), ('subsidy', '\u4ee3\u7406\u8865\u8d34'), ('recruit', '\u62db\u52df\u5956\u91d1'), ('ordred', '\u8ba2\u5355\u7ea2\u5305'), ('flush', '\u8865\u5dee\u989d'), ('recharge', '\u5145\u503c'), ('fan_cary', '\u7c89\u4e1d\u63d0\u6210'), ('grp_bns', '\u56e2\u5458\u5956\u91d1'), ('activity', '\u6d3b\u52a8\u5956\u91d1')], db_index=True, default='rebeta', max_length=8, verbose_name='\u7c7b\u578b'),
        ),
        migrations.AlterField(
            model_name='carrylog',
            name='status',
            field=models.CharField(blank=True, choices=[('pending', '\u5f85\u786e\u8ba4'), ('confirmed', '\u5df2\u786e\u5b9a'), ('canceled', '\u5df2\u53d6\u6d88')], db_index=True, default='confirmed', max_length=16, verbose_name='\u72b6\u6001'),
        ),
    ]
