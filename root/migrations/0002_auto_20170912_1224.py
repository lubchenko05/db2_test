# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-12 12:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('root', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='verified_code',
            field=models.CharField(default='NKKVFVUW', max_length=8),
        ),
    ]
