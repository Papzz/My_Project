# Generated by Django 5.0.1 on 2024-03-12 20:02

import myapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_alter_pakalpojums_apkalposanas_lim_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pakalpojums',
            name='k_parole',
            field=models.CharField(default=myapp.models.generate_random_code, max_length=4),
        ),
        migrations.AlterField(
            model_name='pakalpojums',
            name='r_numurs',
            field=models.CharField(default=myapp.models.generate_unique_seven_digit_code, max_length=7),
        ),
    ]
