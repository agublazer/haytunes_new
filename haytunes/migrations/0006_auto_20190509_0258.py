# Generated by Django 2.2 on 2019-05-09 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('haytunes', '0005_auto_20190509_0141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='id',
            field=models.UUIDField(default='<function uuid4 at 0x7fbba365d840>', help_text='Unique ID for this particular product across', primary_key=True, serialize=False),
        ),
    ]