# Generated by Django 4.1.7 on 2023-02-28 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0005_alter_cart_price_alter_cart_unit_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(db_index=True),
        ),
    ]