# Generated by Django 4.1.7 on 2023-02-26 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0003_alter_category_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='cart',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
    ]
