# Generated by Django 2.0.5 on 2018-06-09 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotifyvis', '0002_auto_20180608_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='name',
            field=models.CharField(max_length=150),
        ),
    ]
