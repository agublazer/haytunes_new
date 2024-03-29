# Generated by Django 2.2.2 on 2019-07-07 03:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('haytunes', '0011_auto_20190706_2155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='number_ratings',
        ),
        migrations.AddField(
            model_name='product',
            name='rated_by',
            field=models.ManyToManyField(blank=True, help_text='Select owners that rated this product.', related_name='users_rated_product', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='product',
            name='owner',
            field=models.ManyToManyField(blank=True, help_text='Select an owner for this product.', related_name='users_bought_product', to=settings.AUTH_USER_MODEL),
        ),
    ]
