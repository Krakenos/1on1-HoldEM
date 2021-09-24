# Generated by Django 3.1.7 on 2021-04-19 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_auto_20210226_0618'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='money',
            field=models.IntegerField(default=2000),
        ),
        migrations.AlterField(
            model_name='player',
            name='score',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]