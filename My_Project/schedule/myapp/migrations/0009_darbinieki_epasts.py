# Generated by Django 5.0.3 on 2024-03-21 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_alter_pakalpojums_k_parole_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='darbinieki',
            name='epasts',
            field=models.EmailField(default='', max_length=50),
        ),
    ]