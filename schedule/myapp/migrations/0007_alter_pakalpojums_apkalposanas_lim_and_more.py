# Generated by Django 5.0.1 on 2024-02-23 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_alter_darbinieki_menedzeris_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pakalpojums',
            name='apkalposanas_lim',
            field=models.SmallIntegerField(default='0'),
        ),
        migrations.AlterField(
            model_name='pakalpojums',
            name='ats_apraksts',
            field=models.TextField(default='0', max_length=150),
        ),
        migrations.AlterField(
            model_name='pakalpojums',
            name='dar_atrums',
            field=models.SmallIntegerField(default='0'),
        ),
        migrations.AlterField(
            model_name='pakalpojums',
            name='darb_apraksts',
            field=models.TextField(default='0', max_length=300),
        ),
        migrations.AlterField(
            model_name='pakalpojums',
            name='darb_kval',
            field=models.SmallIntegerField(default='0'),
        ),
    ]
