# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-30 15:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xiaolumm', '0082_add_show_qrcode_to_flashsale_xlmm_nine_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='xiaolucoinlog',
            name='balance',
            field=models.IntegerField(default=0, verbose_name='\u53d8\u52a8\u540e\u4f59\u989d(\u5206)'),
        ),
    ]
