# Generated by Django 3.1.7 on 2021-04-29 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_auto_20210429_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningdata',
            name='decision',
            field=models.IntegerField(default=1),
        ),
    ]