# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0010_change_sale_suppliers_field_blank_true'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleproductmanagedetail',
            name='schedule_type',
            field=models.CharField(default=b'sale', max_length=16, verbose_name='\u6392\u671f\u7c7b\u578b', db_index=True, choices=[(b'brand', '\u54c1\u724c'), (b'top', 'TOP\u699c'), (b'sale', '\u7279\u5356')]),
        ),
    ]
