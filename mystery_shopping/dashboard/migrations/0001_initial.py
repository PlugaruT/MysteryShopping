# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardComment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=30, null=True, blank=True)),
                ('comment', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='DashboardTemplate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('structure', models.TextField()),
                ('tenant', models.ForeignKey(to='tenants.Tenant')),
            ],
        ),
        migrations.AddField(
            model_name='dashboardcomment',
            name='dashboard',
            field=models.ForeignKey(to='dashboard.DashboardTemplate'),
        ),
    ]
