# Generated by Django 5.1 on 2024-08-14 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MedblockApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='product_images/'),
        ),
    ]
