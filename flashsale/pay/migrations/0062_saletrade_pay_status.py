# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-03 18:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pay', '0061_add_field_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='saletrade',
            name='pay_status',
            field=models.IntegerField(blank=True, choices=[(0, '\u8ba2\u5355\u672a\u652f\u4ed8'), (1, '\u8ba2\u5355\u652f\u4ed8\u4e2d'), (2, '\u8ba2\u5355\u652f\u4ed8\u5b8c\u6210')], db_index=True, default=0, verbose_name='\u652f\u4ed8\u72b6\u6001'),
        ),
    ]
