# Generated by Django 3.1.7 on 2021-05-06 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0009_auto_20210506_1102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='value',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='money_pool',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='money_put',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='opp_money',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='opp_money_put',
            field=models.FloatField(default=0),
        ),
    ]