# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-07-25 13:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('goods', '0002_goodsvisitcount'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0003_auto_20190716_1311'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('count', models.IntegerField(default=1, verbose_name='数量')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='单价')),
                ('comment', models.TextField(default='', verbose_name='评价信息')),
                ('score', models.SmallIntegerField(choices=[(0, '0分'), (1, '20分'), (2, '40分'), (3, '60分'), (4, '80分'), (5, '100分')], default=5, verbose_name='满意度评分')),
                ('is_anonymous', models.BooleanField(default=False, verbose_name='是否匿名评价')),
                ('is_commented', models.BooleanField(default=False, verbose_name='是否评价了')),
            ],
            options={
                'verbose_name_plural': '订单商品',
                'verbose_name': '订单商品',
                'db_table': 'tb_order_goods',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('order_id', models.CharField(max_length=64, primary_key=True, serialize=False, verbose_name='订单号')),
                ('total_count', models.IntegerField(default=1, verbose_name='商品总数')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='商品总金额')),
                ('freight', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='运费')),
                ('pay_method', models.SmallIntegerField(choices=[(1, '货到付款'), (2, '支付宝')], default=1, verbose_name='支付方式')),
                ('status', models.SmallIntegerField(choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成'), (6, '已取消')], default=1, verbose_name='订单状态')),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.Address', verbose_name='收货地址')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='下单用户')),
            ],
            options={
                'verbose_name_plural': '订单基本信息',
                'verbose_name': '订单基本信息',
                'db_table': 'tb_order_info',
            },
        ),
        migrations.AddField(
            model_name='ordergoods',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skus', to='orders.OrderInfo', verbose_name='订单'),
        ),
        migrations.AddField(
            model_name='ordergoods',
            name='sku',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='goods.SKU', verbose_name='订单商品'),
        ),
    ]
