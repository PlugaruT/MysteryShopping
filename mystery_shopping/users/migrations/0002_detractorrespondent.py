# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-12 16:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_auto_20160909_1817'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetractorRespondent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=20)),
                ('surname', models.CharField(blank=True, max_length=30)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=30)),
                ('evaluation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='detractors', to='projects.Evaluation')),
            ],
        ),
    ]
