# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-29 10:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jimay', '0009_jimayagentorder_channel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jimayagentstat',
            name='indirect_sales',
        ),
        migrations.AddField(
            model_name='jimayagentstat',
            name='direct_salenum',
            field=models.IntegerField(default=0, help_text='\u76f4\u63a5\u9500\u552e\u7ec4\u6570', verbose_name='\u76f4\u63a5\u9500\u552e\u7ec4\u6570'),
        ),
        migrations.AlterField(
            model_name='jimayagentorder',
            name='channel',
            field=models.IntegerField(choices=[(0, '\u672a\u77e5\u6e20\u9053'), (1, '\u4e2a\u4eba\u5fae\u4fe1'), (2, '\u4e2a\u4eba\u652f\u4ed8\u5b9d'), (3, '\u94f6\u884c\u8f6c\u8d26')], db_index=True, default=0, verbose_name='\u652f\u4ed8\u6e20\u9053'),
        ),
    ]
