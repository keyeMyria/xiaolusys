# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-13 21:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jimay', '0002_create_jimayagentorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='jimayagentorder',
            name='pic_path',
            field=models.CharField(blank=True, max_length=256, verbose_name='\u5546\u54c1\u56fe\u7247'),
        ),
        migrations.AlterField(
            model_name='jimayagentorder',
            name='total_fee',
            field=models.IntegerField(default=0, help_text='\u7cbe\u5ea6\u5206', verbose_name='\u5546\u54c1\u603b\u4ef7'),
        ),
    ]
