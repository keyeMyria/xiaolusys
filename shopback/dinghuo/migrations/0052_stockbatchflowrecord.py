# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-13 15:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dinghuo', '0051_change_batch_no_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockBatchFlowRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('modified', models.DateTimeField(auto_now=True, db_index=True, verbose_name='\u4fee\u6539\u65e5\u671f')),
                ('model_id', models.IntegerField(db_index=True, verbose_name='\u6b3e\u5f0fID')),
                ('sku_id', models.IntegerField(db_index=True, verbose_name='\u89c4\u683cID')),
                ('record_num', models.IntegerField(default=0, verbose_name='\u8bb0\u5f55\u6570\u91cf')),
                ('record_type', models.CharField(choices=[('sorder', '\u7279\u5356\u8ba2\u5355'), ('srefund', '\u9000\u8d27\u8ba2\u5355')], db_index=True, max_length=8, verbose_name='\u8bb0\u5f55\u7c7b\u578b')),
                ('batch_no', models.CharField(db_index=True, max_length=16, verbose_name='\u6279\u6b21\u7f16\u53f7')),
                ('referal_id', models.CharField(db_index=True, max_length=32, verbose_name='\u5173\u8054ID')),
                ('uni_key', models.CharField(max_length=32, unique=True, verbose_name='\u552f\u4e00\u952e')),
                ('status', models.BooleanField(db_index=True, default=False, verbose_name='\u662f\u5426\u6709\u6548')),
                ('finish_time', models.DateTimeField(db_index=True, blank=True, null=True, verbose_name='\u5b8c\u6210\u65f6\u95f4')),
            ],
            options={
                'db_table': 'flashsale_dinghuo_stockflow',
                'verbose_name': '\u5e93\u5b58|\u6279\u6b21\u6d41\u52a8\u8bb0\u5f55',
                'verbose_name_plural': '\u5e93\u5b58|\u6279\u6b21\u6d41\u52a8\u8bb0\u5f55\u5217\u8868',
            },
        ),
    ]
