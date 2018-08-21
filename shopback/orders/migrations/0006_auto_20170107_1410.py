# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-07 14:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_trade_unikey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='user_address_unikey',
            field=models.CharField(db_index=True, default=None, help_text='\u7528\u6237\u5730\u5740sha1', max_length=40, null=True, verbose_name='\u5730\u5740\u552f\u4e00\u6807\u8bc6'),
        ),
        migrations.AlterField(
            model_name='trade',
            name='user_unikey',
            field=models.CharField(db_index=True, default=None, help_text='\u7528\u6237\u59d3\u540d\u7535\u8bddsha1', max_length=40, null=True, verbose_name='\u7528\u6237\u552f\u4e00\u6807\u8bc6'),
        ),
    ]