# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-21 17:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0038_auto_20161213_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesupplier',
            name='return_ware_by',
            field=models.SmallIntegerField(choices=[(0, '\u672a\u9009\u4ed3'), (1, '\u4e0a\u6d77\u4ed3'), (2, '\u5e7f\u5dde\u4ed3'), (3, '\u516c\u53f8\u4ed3'), (9, '\u7b2c\u4e09\u65b9\u4ed3')], default=1, verbose_name='\u9000\u8d27\u4ed3\u5e93'),
        ),
    ]
