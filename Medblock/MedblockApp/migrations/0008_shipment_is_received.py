# Generated by Django 5.1.1 on 2024-10-10 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MedblockApp', '0007_shipment_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='is_received',
            field=models.BooleanField(default=True),
        ),
    ]
