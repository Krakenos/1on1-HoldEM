# Generated by Django 3.1.7 on 2021-04-29 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_auto_20210429_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningdata',
            name='card_1_suit',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='card_1_val',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='card_2_suit',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='card_2_val',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='card_3_suit',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='card_3_val',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='card_4_suit',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='card_4_val',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='card_5_suit',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='card_5_val',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='learningdata',
            name='total_money',
            field=models.IntegerField(default=0),
        ),
    ]