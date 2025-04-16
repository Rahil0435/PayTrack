# Generated by Django 5.1.5 on 2025-04-12 17:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app2', '0009_alter_invoice2_balance_amount_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentRecord2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField(auto_now_add=True)),
                ('mode', models.CharField(blank=True, max_length=100)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='app2.invoice2')),
            ],
        ),
    ]
