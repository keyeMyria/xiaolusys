# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-15 11:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clickcount', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clicks',
            name='click_url',
            field=models.CharField(blank=True, max_length=128, verbose_name='\u70b9\u51fburl'),
        ),
    ]