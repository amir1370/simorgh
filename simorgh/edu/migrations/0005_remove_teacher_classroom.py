# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-25 12:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edu', '0004_auto_20190425_1558'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='classroom',
        ),
    ]
