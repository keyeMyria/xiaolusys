# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-04 10:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20161118_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='stage',
            field=models.IntegerField(choices=[(0, '\u9700\u521b\u5efaPackageSkuItem'), (1, '\u5df2\u521b\u5efa'), (2, '\u5df2\u5b8c\u7ed3')], default=0, help_text='0\u672a\u5904\u74061\u53d1\u8d27\u4e2d2\u5df2\u5b8c\u7ed3', verbose_name='\u53d1\u8d27\u8fdb\u5ea6'),
        ),
    ]
