# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-06-01 10:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edu', '0015_assignment'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='description',
            field=models.TextField(default=-1.0),
            preserve_default=False,
        ),
    ]