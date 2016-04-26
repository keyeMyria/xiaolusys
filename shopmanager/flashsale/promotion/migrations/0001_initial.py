# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pay', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppDownloadRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('from_customer', models.IntegerField(default=0, verbose_name='\u6765\u81ea\u7528\u6237', db_index=True)),
                ('openid', models.CharField(db_index=True, max_length=128, null=True, verbose_name='\u5fae\u4fe1\u6388\u6743openid', blank=True)),
                ('unionid', models.CharField(db_index=True, max_length=128, null=True, verbose_name='\u5fae\u4fe1\u6388\u6743unionid', blank=True)),
                ('status', models.BooleanField(default=0, verbose_name='\u662f\u5426\u6ce8\u518cAPP', db_index=True, choices=[(0, '\u672a\u6ce8\u518c'), (1, '\u5df2\u6ce8\u518c')])),
                ('mobile', models.CharField(db_index=True, max_length=11, null=True, verbose_name='\u624b\u673a\u53f7', blank=True)),
                ('ufrom', models.CharField(max_length=8, verbose_name='\u6765\u81ea\u5e73\u53f0', choices=[(b'wap', '\u5fae\u4fe1'), (b'wap', '\u670b\u53cb\u5708'), (b'wap', '\u65b0\u6d6a\u5fae\u535a'), (b'wap', 'WAP'), (b'wap', 'QQ\u7a7a\u95f4'), (b'wap', '\u5c0f\u9e7f\u7f8e\u7f8eapp')])),
            ],
            options={
                'db_table': 'flashsale_promotion_download_record',
                'verbose_name': '\u63a8\u5e7f/\u4e0b\u8f7d\u8bb0\u5f55\u8868',
                'verbose_name_plural': '\u63a8\u5e7f/\u4e0b\u8f7d\u8bb0\u5f55\u8868',
            },
        ),
        migrations.CreateModel(
            name='AwardWinner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('customer_id', models.IntegerField(default=0, verbose_name='\u7528\u6237ID', db_index=True)),
                ('customer_img', models.CharField(max_length=256, null=True, verbose_name='\u5934\u50cf', blank=True)),
                ('customer_nick', models.CharField(max_length=64, null=True, verbose_name='\u6635\u79f0', blank=True)),
                ('event_id', models.IntegerField(db_index=True, null=True, verbose_name='\u6d3b\u52a8ID', blank=True)),
                ('invite_num', models.IntegerField(default=0, verbose_name='\u4e2d\u5956\u65f6\u9080\u8bf7\u6570')),
                ('uni_key', models.CharField(unique=True, max_length=128, verbose_name='\u552f\u4e00ID', blank=True)),
                ('status', models.IntegerField(default=0, verbose_name='\u9886\u53d6\u72b6\u6001', choices=[(0, b'\xe6\x9c\xaa\xe9\xa2\x86\xe5\x8f\x96'), (1, b'\xe5\xb7\xb2\xe9\xa2\x86\xe5\x8f\x96')])),
            ],
            options={
                'db_table': 'flashsale_promotion_award_winner',
                'verbose_name': '\u6d3b\u52a8/\u4e2d\u5956',
                'verbose_name_plural': '\u6d3b\u52a8/\u4e2d\u5956\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='DressProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('age_min', models.IntegerField(verbose_name='\u5e74\u9f84\u5927\u7b49\u4e8e', db_index=True)),
                ('age_max', models.IntegerField(verbose_name='\u5e74\u9f84\u5c0f\u7b49\u4e8e')),
                ('category', models.IntegerField(verbose_name='\u5206\u7c7bID')),
                ('product_id', models.BigIntegerField(verbose_name='\u63a8\u8350\u5546\u54c1ID')),
                ('in_active', models.BooleanField(verbose_name='\u751f\u6548')),
            ],
            options={
                'db_table': 'flashsale_mmexam_dressproduct',
                'verbose_name': '\u63a8\u5e7f/\u7a7f\u8863\u6d4b\u8bd5\u63a8\u8350\u5546\u54c1',
                'verbose_name_plural': '\u63a8\u5e7f/\u7a7f\u8863\u6d4b\u8bd5\u63a8\u8350\u5546\u54c1\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='MamaDressResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('user_unionid', models.CharField(unique=True, max_length=28, verbose_name='\u7528\u6237Unionid')),
                ('openid', models.CharField(max_length=28, verbose_name='\u7528\u6237openid')),
                ('mama_age', models.IntegerField(default=0, verbose_name='\u5988\u5988\u5e74\u9f84')),
                ('mama_headimg', models.CharField(max_length=256, verbose_name='\u5934\u50cf')),
                ('mama_nick', models.CharField(max_length=32, verbose_name='\u6635\u79f0')),
                ('referal_from', models.CharField(db_index=True, max_length=28, verbose_name='\u63a8\u8350\u4ebaUnoinid', blank=True)),
                ('exam_score', models.IntegerField(default=0, verbose_name='\u7b54\u9898\u5206\u6570')),
                ('share_from', models.CharField(max_length=64, verbose_name='\u5206\u4eab\u5e73\u53f0')),
                ('exam_date', models.DateTimeField(auto_now_add=True, verbose_name='\u7b54\u9898\u65e5\u671f', null=True)),
                ('exam_state', models.IntegerField(default=0, verbose_name='\u72b6\u6001', choices=[(0, '\u672a\u5b8c\u6210'), (1, '\u5df2\u5b8c\u6210')])),
            ],
            options={
                'db_table': 'flashsale_mmexam_dressresult',
                'verbose_name': '\u63a8\u5e7f/\u7a7f\u8863\u98ce\u683c\u6d4b\u8bd5\u7ed3\u679c',
                'verbose_name_plural': '\u63a8\u5e7f/\u7a7f\u8863\u98ce\u683c\u6d4b\u8bd5\u7ed3\u679c\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='ReadPacket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('customer', models.CharField(max_length=64, verbose_name='\u7528\u6237ID', db_index=True)),
                ('value', models.FloatField(default=0, verbose_name='\u91d1\u989d')),
                ('status', models.IntegerField(default=0, verbose_name='\u662f\u5426\u5151\u6362', choices=[(1, '\u5df2\u6253\u5f00'), (0, '\u672a\u6253\u5f00')])),
                ('content', models.CharField(max_length=512, null=True, verbose_name='\u6587\u5b57\u5185\u5bb9', blank=True)),
            ],
            options={
                'db_table': 'flashsale_promotion_red_packet',
                'verbose_name': '\u63a8\u5e7f/discard',
                'verbose_name_plural': '\u63a8\u5e7f/discard',
            },
        ),
        migrations.CreateModel(
            name='RedEnvelope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('customer_id', models.IntegerField(default=0, verbose_name='\u7528\u6237ID', db_index=True)),
                ('event_id', models.IntegerField(db_index=True, null=True, verbose_name='\u6d3b\u52a8ID', blank=True)),
                ('value', models.IntegerField(default=0, verbose_name='\u91d1\u989d')),
                ('description', models.CharField(max_length=128, null=True, verbose_name='\u6587\u5b57\u5185\u5bb9', blank=True)),
                ('uni_key', models.CharField(unique=True, max_length=128, verbose_name='\u552f\u4e00ID', blank=True)),
                ('friend_img', models.CharField(max_length=256, null=True, verbose_name='\u670b\u53cb\u5934\u50cf', blank=True)),
                ('friend_nick', models.CharField(max_length=64, null=True, verbose_name='\u670b\u53cb\u6635\u79f0', blank=True)),
                ('type', models.IntegerField(default=0, db_index=True, verbose_name='\u7c7b\u578b', choices=[(0, b'cash'), (1, b'card')])),
                ('status', models.IntegerField(default=0, db_index=True, verbose_name='\u6253\u5f00\u72b6\u6001', choices=[(0, b'new'), (1, b'open')])),
            ],
            options={
                'db_table': 'flashsale_promotion_red_envelope',
                'verbose_name': '\u6d3b\u52a8/\u7ea2\u5305',
                'verbose_name_plural': '\u6d3b\u52a8/\u7ea2\u5305\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='XLFreeSample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('outer_id', models.CharField(max_length=64, verbose_name='\u5546\u54c1\u7f16\u7801', blank=True)),
                ('name', models.CharField(max_length=64, verbose_name='\u6d3b\u52a8\u540d\u79f0', blank=True)),
                ('expiried', models.DateTimeField(verbose_name='\u8fc7\u671f\u65f6\u95f4')),
                ('pic_url', models.URLField(verbose_name=b'\xe5\x95\x86\xe5\x93\x81\xe5\x9b\xbe\xe7\x89\x87', blank=True)),
                ('sale_url', models.URLField(verbose_name=b'\xe9\x94\x80\xe5\x94\xae\xe9\x93\xbe\xe6\x8e\xa5', blank=True)),
            ],
            options={
                'db_table': 'flashsale_promotion_freesample',
                'verbose_name': '\u63a8\u5e7f/\u8bd5\u7528\u5546\u54c1',
                'verbose_name_plural': '\u63a8\u5e7f/\u8bd5\u7528\u5546\u54c1\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='XLInviteCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('mobile', models.CharField(unique=True, max_length=11, verbose_name='\u624b\u673a\u53f7\u7801')),
                ('vipcode', models.CharField(unique=True, max_length=16, verbose_name='\u9080\u8bf7\u7801')),
                ('expiried', models.DateTimeField(verbose_name='\u8fc7\u671f\u65f6\u95f4')),
                ('code_type', models.IntegerField(default=0, verbose_name='\u9080\u8bf7\u7801\u7c7b\u578b', choices=[(0, '\u514d\u8d39\u8bd5\u7528'), (1, '\u62db\u52df\u4ee3\u7406')])),
                ('code_rule', models.CharField(max_length=256, verbose_name='\u4f7f\u7528\u89c4\u5219', blank=True)),
                ('max_usage', models.IntegerField(default=0, verbose_name='\u53ef\u7528\u6b21\u6570')),
                ('usage_count', models.IntegerField(default=0, verbose_name='\u5df2\u4f7f\u7528', db_index=True)),
            ],
            options={
                'db_table': 'flashsale_promotion_invitecode',
                'verbose_name': '\u63a8\u5e7f/\u6d3b\u52a8\u9080\u8bf7\u7801',
                'verbose_name_plural': '\u63a8\u5e7f/\u6d3b\u52a8\u9080\u8bf7\u7801\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='XLInviteCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('apply_count', models.IntegerField(default=0, verbose_name='\u7533\u8bf7\u4eba\u6570')),
                ('invite_count', models.IntegerField(default=0, verbose_name='\u6fc0\u6d3b\u4eba\u6570')),
                ('click_count', models.IntegerField(default=0, verbose_name='\u70b9\u51fb\u6b21\u6570')),
                ('customer', models.OneToOneField(verbose_name='\u7279\u5356\u7528\u6237', to='pay.Customer')),
            ],
            options={
                'db_table': 'flashsale_promotion_invitecount',
                'verbose_name': '\u63a8\u5e7f/\u6d3b\u52a8\u9080\u8bf7\u7ed3\u679c',
                'verbose_name_plural': '\u63a8\u5e7f/\u6d3b\u52a8\u9080\u8bf7\u7ed3\u679c\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='XLReferalRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('referal_uid', models.CharField(unique=True, max_length=64, verbose_name='\u88ab\u63a8\u8350\u4ebaID')),
                ('referal_from_uid', models.CharField(max_length=64, verbose_name='\u63a8\u8350\u4ebaID', db_index=True)),
            ],
            options={
                'db_table': 'flashsale_promotion_relationship',
                'verbose_name': '\u63a8\u5e7f/\u7528\u6237\u9080\u8bf7\u5173\u7cfb',
                'verbose_name_plural': '\u63a8\u5e7f/\u7528\u6237\u9080\u8bf7\u5173\u7cfb',
            },
        ),
        migrations.CreateModel(
            name='XLSampleApply',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('outer_id', models.CharField(max_length=32, verbose_name='\u5546\u54c1\u7f16\u7801', blank=True)),
                ('sku_code', models.CharField(max_length=32, verbose_name='SKU\u7f16\u7801', blank=True)),
                ('event_id', models.IntegerField(db_index=True, null=True, verbose_name='\u6d3b\u52a8ID', blank=True)),
                ('from_customer', models.BigIntegerField(db_index=True, null=True, verbose_name='\u5206\u4eab\u4eba\u7528\u6237ID', blank=True)),
                ('ufrom', models.CharField(blank=True, max_length=8, verbose_name='\u6765\u81ea\u5e73\u53f0', choices=[(b'wxapp', '\u5fae\u4fe1\u597d\u53cb'), (b'pyq', '\u670b\u53cb\u5708'), (b'qq', 'QQ'), (b'sinawb', '\u65b0\u6d6a\u5fae\u535a'), (b'web', '\u5916\u90e8\u7f51\u9875'), (b'app', '\u5c0f\u9e7f\u7f8e\u7f8eAPP')])),
                ('user_openid', models.CharField(db_index=True, max_length=28, null=True, verbose_name='\u7528\u6237openid', blank=True)),
                ('user_unionid', models.CharField(db_index=True, max_length=64, null=True, verbose_name='\u7528\u6237unionid', blank=True)),
                ('mobile', models.CharField(max_length=11, verbose_name='\u8bd5\u7528\u624b\u673a', db_index=True)),
                ('vipcode', models.CharField(db_index=True, max_length=16, null=True, verbose_name='\u8bd5\u7528\u9080\u8bf7\u7801', blank=True)),
                ('status', models.IntegerField(default=0, db_index=True, verbose_name='\u72b6\u6001', choices=[(0, '\u672a\u6fc0\u6d3b'), (1, '\u5df2\u6fc0\u6d3b')])),
                ('customer_id', models.IntegerField(null=True, verbose_name='\u7533\u8bf7\u8005ID', blank=True)),
                ('headimgurl', models.CharField(max_length=256, verbose_name='\u5934\u56fe', blank=True)),
                ('nick', models.CharField(max_length=32, verbose_name='\u6635\u79f0', blank=True)),
            ],
            options={
                'db_table': 'flashsale_promotion_sampleapply',
                'verbose_name': '\u63a8\u5e7f/\u8bd5\u7528\u7533\u8bf7',
                'verbose_name_plural': '\u63a8\u5e7f/\u8bd5\u7528\u7533\u8bf7\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='XLSampleOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('xlsp_apply', models.IntegerField(default=0, db_index=True, verbose_name='\u8bd5\u7528\u7533\u8bf7id', blank=True)),
                ('customer_id', models.CharField(max_length=64, verbose_name='\u7528\u6237ID', db_index=True)),
                ('outer_id', models.CharField(max_length=32, verbose_name='\u5546\u54c1\u7f16\u7801', blank=True)),
                ('sku_code', models.CharField(max_length=32, verbose_name='SKU\u7f16\u7801', blank=True)),
                ('vipcode', models.CharField(max_length=16, verbose_name='\u8bd5\u7528\u9080\u8bf7\u7801', db_index=True)),
                ('problem_score', models.IntegerField(default=0, verbose_name='\u7b54\u9898\u5206\u6570')),
                ('status', models.IntegerField(default=0, verbose_name='\u4e2d\u5956\u6279\u6b21', db_index=True)),
                ('award_status', models.BooleanField(default=False, db_index=True, verbose_name=b'\xe9\xa2\x86\xe5\x8f\x96\xe5\xa5\x96\xe5\x93\x81')),
            ],
            options={
                'db_table': 'flashsale_promotion_sampleorder',
                'verbose_name': '\u63a8\u5e7f/\u8bd5\u7528\u8ba2\u5355',
                'verbose_name_plural': '\u63a8\u5e7f/\u8bd5\u7528\u8ba2\u5355\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='XLSampleSku',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f', db_index=True)),
                ('sku_code', models.CharField(max_length=32, verbose_name='SKU\u7f16\u7801', blank=True)),
                ('sku_name', models.CharField(max_length=64, verbose_name='\u6b3e\u5f0f\u5c3a\u5bf8', blank=True)),
                ('sample_product', models.ForeignKey(related_name='skus', verbose_name='\u8bd5\u7528\u5546\u54c1', to='promotion.XLFreeSample')),
            ],
            options={
                'db_table': 'flashsale_promotion_samplesku',
                'verbose_name': '\u63a8\u5e7f/\u8bd5\u7528\u5546\u54c1SKU',
                'verbose_name_plural': '\u63a8\u5e7f/\u8bd5\u7528\u5546\u54c1SKU\u5217\u8868',
            },
        ),
    ]