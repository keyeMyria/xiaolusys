# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pay', '0028_add_price_to_flashsale_favorites'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='first_paytime',
            field=models.DateTimeField(null=True, verbose_name='\u9996\u6b21\u8d2d\u4e70\u65e5\u671f', blank=True),
        ),
    ]
