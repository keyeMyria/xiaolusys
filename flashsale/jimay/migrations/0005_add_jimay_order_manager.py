# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-16 14:57
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jimay', '0004_add_logistics'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jimayagentorder',
            options={'verbose_name': '\u5df1\u7f8e\u533b\u5b66/\u8ba2\u8d27\u8bb0\u5f55', 'verbose_name_plural': '\u5df1\u7f8e\u533b\u5b66/\u8ba2\u8d27\u8bb0\u5f55'},
        ),
        migrations.AddField(
            model_name='jimayagentorder',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='\u7ba1\u7406\u5458'),
        ),
        migrations.AlterField(
            model_name='jimayagentorder',
            name='logistic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='logistics.LogisticsCompany', verbose_name='\u7269\u6d41\u516c\u53f8'),
        ),
        migrations.AlterField(
            model_name='jimayagentorder',
            name='payment',
            field=models.IntegerField(default=0, help_text='\u7cbe\u5ea6\u5206,\u73b0\u9ed8\u8ba4\u7531\u8fd0\u8425\u4eba\u5458\u586b\u5199', verbose_name='\u652f\u4ed8\u91d1\u989d(\u5206)'),
        ),
        migrations.AlterField(
            model_name='jimayagentorder',
            name='status',
            field=models.IntegerField(choices=[(0, '\u5df2\u7533\u8bf7'), (1, '\u5df2\u63a5\u5355'), (2, '\u5df2\u4ed8\u6b3e'), (3, '\u5df2\u53d1\u8d27'), (4, '\u5df2\u5b8c\u6210'), (5, '\u5df2\u53d6\u6d88')], db_index=True, default=0, verbose_name='\u72b6\u6001'),
        ),
        migrations.AlterField(
            model_name='jimayagentorder',
            name='total_fee',
            field=models.IntegerField(default=0, help_text='\u7cbe\u5ea6\u5206', verbose_name='\u5546\u54c1\u603b\u4ef7(\u5206)'),
        ),
    ]
