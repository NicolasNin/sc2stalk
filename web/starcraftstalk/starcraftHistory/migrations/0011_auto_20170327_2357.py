# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-27 23:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starcraftHistory', '0010_auto_20170316_0006'),
    ]

    operations = [
        migrations.AddField(
            model_name='progamer',
            name='truename',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='progamer',
            name='wcsregion',
            field=models.CharField(blank=True, db_column='wcsregion', max_length=45, null=True),
        ),
    ]