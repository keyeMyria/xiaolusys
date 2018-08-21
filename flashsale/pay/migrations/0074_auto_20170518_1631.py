# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-18 16:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pay', '0073_add_table_bankaccount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='\u521b\u5efa\u65f6\u95f4'),
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='status',
            field=models.SmallIntegerField(choices=[(0, '\u6b63\u5e38'), (1, '\u4f5c\u5e9f')], db_index=True, default=0, verbose_name='\u72b6\u6001'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='districtversion',
            name='download_url',
            field=models.CharField(blank=True, help_text='\u4e0d\u7528\u586b\u5199,\u7b2c\u4e8c\u6b21\u4fdd\u5b58\u65f6\u4f1a\u81ea\u52a8\u751f\u6210', max_length=256, verbose_name='\u4e0b\u8f7d\u94fe\u63a5'),
        ),
        migrations.AlterField(
            model_name='districtversion',
            name='hash256',
            field=models.CharField(blank=True, help_text='\u4e0d\u7528\u586b\u5199,\u7b2c\u4e8c\u6b21\u4fdd\u5b58\u65f6\u4f1a\u81ea\u52a8\u751f\u6210', max_length=128, verbose_name='sha1\u503c'),
        ),
        migrations.AlterField(
            model_name='districtversion',
            name='memo',
            field=models.TextField(blank=True, help_text='\u9700\u586b\u5199', verbose_name='\u5907\u6ce8'),
        ),
        migrations.AlterField(
            model_name='districtversion',
            name='status',
            field=models.BooleanField(default=False, help_text='\u9700\u52fe\u9009,\u8868\u793a\u9700\u8981\u9a6c\u4e0a\u66f4\u65b0', verbose_name='\u751f\u6548'),
        ),
        migrations.AlterField(
            model_name='districtversion',
            name='version',
            field=models.CharField(help_text='\u9700\u586b\u5199', max_length=32, unique=True, verbose_name='\u7248\u672c\u53f7'),
        ),
        migrations.AlterField(
            model_name='modelproduct',
            name='head_imgs',
            field=models.TextField(blank=True, help_text='\u5546\u54c1\u5206\u4eab\u5c55\u793a\u56fe\u7247(\u53d6\u9996\u5f20)', verbose_name='\u9898\u5934\u7167(\u591a\u5f20\u8bf7\u6362\u884c)'),
        ),
        migrations.AlterField(
            model_name='saletrade',
            name='budget_paid',
            field=models.FloatField(default=0.0, help_text='\u94b1\u5305\u4f59\u989d\u652f\u4ed8\u91d1\u989d', verbose_name='\u4f59\u989d\u652f\u4ed8'),
        ),
        migrations.AlterField(
            model_name='saletrade',
            name='pay_cash',
            field=models.FloatField(default=0.0, help_text='\u53ea\u5305\u542b\u73b0\u91d1\uff0c\u4e0d\u5305\u542b\u94b1\u5305\u652f\u4ed8\u91d1\u989d\u7b49', verbose_name='\u5b9e\u4ed8\u73b0\u91d1'),
        ),
    ]
