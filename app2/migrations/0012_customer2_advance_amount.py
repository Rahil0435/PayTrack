# Generated by Django 5.1.5 on 2025-05-21 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app2', '0011_invoice2_original_money_got'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer2',
            name='advance_amount',
            field=models.IntegerField(default=0, help_text='Advance amount paid by the customer'),
        ),
    ]
