# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-13 16:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import flashsale.jimay.models


class Migration(migrations.Migration):

    dependencies = [
        ('pay', '0074_auto_20170518_1631'),
        ('jimay', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JimayAgentOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.CharField(default=flashsale.jimay.models.gen_uuid_order_no, max_length=24, unique=True, verbose_name='\u8ba2\u5355\u7f16\u53f7')),
                ('title', models.CharField(blank=True, max_length=64, verbose_name='\u5546\u54c1\u540d\u79f0')),
                ('model_id', models.IntegerField(default=0, verbose_name='\u6b3e\u5f0fID')),
                ('sku_id', models.IntegerField(default=0, verbose_name='SKUID')),
                ('num', models.IntegerField(default=0, verbose_name='\u6570\u91cf')),
                ('total_fee', models.IntegerField(default=0, verbose_name='\u5546\u54c1\u603b\u4ef7')),
                ('payment', models.IntegerField(default=0, help_text='\u7cbe\u5ea6\u5206,\u73b0\u9ed8\u8ba4\u7531\u8fd0\u8425\u4eba\u5458\u586b\u5199', verbose_name='\u652f\u4ed8\u91d1\u989d')),
                ('status', models.IntegerField(choices=[(0, '\u5df2\u7533\u8bf7'), (1, '\u5df2\u63a5\u5355'), (2, '\u5df2\u4ed8\u6b3e'), (3, '\u5df2\u53d1\u8d27'), (4, '\u5df2\u5b8c\u6210')], db_index=True, default=0, verbose_name='\u72b6\u6001')),
                ('ensure_time', models.DateTimeField(blank=True, null=True, verbose_name='\u5ba1\u6838\u65f6\u95f4')),
                ('pay_time', models.DateTimeField(blank=True, null=True, verbose_name='\u4ed8\u6b3e\u65f6\u95f4')),
                ('send_time', models.DateTimeField(blank=True, null=True, verbose_name='\u53d1\u8d27\u65f6\u95f4')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f')),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pay.UserAddress', verbose_name='\u7528\u6237\u5730\u5740')),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pay.Customer', verbose_name='\u539f\u59cb\u7528\u6237')),
            ],
            options={
                'db_table': 'jimay_agentorder',
                'verbose_name': '\u5df1\u7f8e\u533b\u5b66/\u5355\u54c1\u8ba2\u5355',
                'verbose_name_plural': '\u5df1\u7f8e\u533b\u5b66/\u5355\u54c1\u8ba2\u5355',
            },
        ),
        migrations.AddField(
            model_name='jimayagent',
            name='manager',
            field=models.CharField(blank=True, db_index=True, max_length=24, verbose_name='\u7ba1\u7406\u5458'),
        ),
        migrations.AddField(
            model_name='jimayagent',
            name='unionid',
            field=models.CharField(blank=True, db_index=True, help_text='\u5fae\u4fe1unionid', max_length=32, verbose_name='UNIONID'),
        ),
        migrations.AlterField(
            model_name='jimayagent',
            name='certification',
            field=models.CharField(blank=True, help_text='\u6682\u4e0d\u4f7f\u7528\u94fe\u63a5', max_length=256, verbose_name='\u8bc1\u4e66\u5730\u5740'),
        ),
        migrations.AlterField(
            model_name='jimayagent',
            name='parent_agent_id',
            field=models.IntegerField(db_index=True, default=0, verbose_name='\u7236\u7ea7\u7279\u7ea6\u4ee3\u7406ID'),
        ),
    ]
