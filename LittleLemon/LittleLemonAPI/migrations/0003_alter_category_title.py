# Generated by Django 4.1.7 on 2023-02-25 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0002_alter_category_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='title',
            field=models.CharField(db_index=True, max_length=255),
        ),
    ]
