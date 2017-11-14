# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-10-12 06:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(db_index=True, max_length=30)),
                ('name', models.CharField(db_index=True, max_length=50)),
            ],
        ),
    ]