# Generated by Django 2.2.2 on 2019-07-07 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('haytunes', '0014_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='downloads',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='downloads',
            field=models.IntegerField(default=0),
        ),
    ]
