# Generated by Django 2.2.5 on 2019-09-24 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pick',
            name='response',
            field=models.BooleanField(null=True),
        ),
    ]
