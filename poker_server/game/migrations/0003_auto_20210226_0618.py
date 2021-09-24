# Generated by Django 3.1.7 on 2021-02-26 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_player_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='state',
            field=models.IntegerField(blank=True, default=0, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='score',
            field=models.IntegerField(blank=True, default=0, max_length=2000, null=True),
        ),
    ]
