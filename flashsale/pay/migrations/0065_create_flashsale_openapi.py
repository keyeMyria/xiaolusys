# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-07 11:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pay', '0064_add_fields_useraddress_extras'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenAPI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('modified', models.DateTimeField(auto_now=True, db_index=True, verbose_name='\u4fee\u6539\u65e5\u671f')),
                ('app_id', models.CharField(db_index=True, max_length=16, unique=True, verbose_name='\u5e94\u7528 ID')),
                ('app_secret', models.CharField(max_length=32, verbose_name='\u5e94\u7528 SECRET')),
                ('name', models.CharField(blank=True, db_index=True, max_length=32, verbose_name='\u5e94\u7528\u540d\u79f0')),
            ],
            options={
                'db_table': 'flashsale_openapi',
            },
        ),
    ]
