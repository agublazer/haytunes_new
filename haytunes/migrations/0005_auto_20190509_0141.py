# Generated by Django 2.2 on 2019-05-09 06:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('haytunes', '0004_product_content'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'permissions': (('can_admin_content', 'Admin content in page'),)},
        ),
    ]