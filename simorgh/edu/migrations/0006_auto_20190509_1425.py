# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-09 09:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edu', '0005_remove_teacher_classroom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentcourse',
            name='final_grade',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='studentcourse',
            name='mid_grade',
            field=models.FloatField(null=True),
        ),
    ]