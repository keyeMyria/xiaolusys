# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-12 18:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xiaolumm', '0085_add_exchange_saleorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangesaleorder',
            name='uni_key',
            field=models.CharField(blank=True, max_length=128, unique=True, verbose_name='\u552f\u4e00ID'),
        ),
    ]