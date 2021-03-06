# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-24 22:34
from __future__ import unicode_literals

from django.db import migrations, models
import pms.supplier.models.supplier


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0044_sale_product_relation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salecategory',
            name='grade',
            field=models.IntegerField(db_index=True, default=1, verbose_name='\u7c7b\u76ee\u7b49\u7ea7'),
        ),
        migrations.AlterField(
            model_name='salesupplier',
            name='return_ware_by',
            field=models.SmallIntegerField(choices=[(0, '\u672a\u9009\u4ed3'), (1, '\u4e0a\u6d77\u4ed3'), (2, '\u5e7f\u5dde\u4ed3'), (3, '\u516c\u53f8\u4ed3'), (4, '\u8702\u5de2\u82cf\u5dde\u4ed3'), (5, '\u8702\u5de2\u5e7f\u5dde\u4ed3'), (9, '\u7b2c\u4e09\u65b9\u4ed3'), (10, '\u8702\u5de2\u5341\u91cc\u6d0b\u573a')], default=1, verbose_name='\u9000\u8d27\u4ed3\u5e93'),
        ),
        migrations.AlterField(
            model_name='salesupplier',
            name='supplier_name',
            field=models.CharField(max_length=64, unique=True, verbose_name='\u4f9b\u5e94\u5546\u540d'),
        ),
        migrations.AlterField(
            model_name='salesupplier',
            name='vendor_code',
            field=models.CharField(blank=True, default=pms.supplier.models.supplier.gen_vendor_code, help_text='\u540e\u9762\u5e94\u6539\u4e3aunique', max_length=32, unique=True, verbose_name='\u4f9b\u5e94\u5546\u7f16\u7801'),
        ),
        migrations.AlterField(
            model_name='salesupplier',
            name='ware_by',
            field=models.SmallIntegerField(choices=[(0, '\u672a\u9009\u4ed3'), (1, '\u4e0a\u6d77\u4ed3'), (2, '\u5e7f\u5dde\u4ed3'), (3, '\u516c\u53f8\u4ed3'), (4, '\u8702\u5de2\u82cf\u5dde\u4ed3'), (5, '\u8702\u5de2\u5e7f\u5dde\u4ed3'), (9, '\u7b2c\u4e09\u65b9\u4ed3'), (10, '\u8702\u5de2\u5341\u91cc\u6d0b\u573a')], default=1, verbose_name='\u6240\u5c5e\u4ed3\u5e93'),
        ),
    ]
