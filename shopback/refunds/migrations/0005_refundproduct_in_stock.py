# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-26 14:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('refunds', '0004_add_index_to_sku_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='refundproduct',
            name='in_stock',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u8ba1\u5165\u5e93\u5b58'),
        ),
    ]