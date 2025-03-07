# Generated by Django 5.1.5 on 2025-01-27 17:56

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_alter_event_options_alter_galleryimage_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketPurchase',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_email', models.EmailField(max_length=254)),
                ('quantity', models.IntegerField()),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(choices=[('PENDING', 'Pending'), ('SUCCESS', 'Success'), ('FAILED', 'Failed')], default='PENDING', max_length=20)),
                ('stripe_payment_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event_ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='events.eventticket')),
            ],
            options={
                'verbose_name': 'Ticket Purchase',
                'verbose_name_plural': 'Ticket Purchases',
                'db_table': 'ticket_purchases',
            },
        ),
    ]
