# Generated by Django 2.2.5 on 2019-09-18 01:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('password', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin', models.BooleanField(default=False)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ui.League')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PropBet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('answer', models.BooleanField(null=True)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ui.League')),
            ],
        ),
        migrations.CreateModel(
            name='Pick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.BooleanField()),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ui.Member')),
                ('prop_bet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ui.PropBet')),
            ],
        ),
    ]