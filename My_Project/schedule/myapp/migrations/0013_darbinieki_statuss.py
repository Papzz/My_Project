# Generated by Django 5.0.3 on 2024-03-26 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_paktip_pakalpojums_statuss_pakalpojums_paktip_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='darbinieki',
            name='statuss',
            field=models.BooleanField(default=False),
        ),
    ]
