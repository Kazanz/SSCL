# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-25 23:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0003_person_football'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Person',
            new_name='Waiver',
        ),
    ]
