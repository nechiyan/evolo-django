# Generated by Django 5.1.5 on 2025-01-23 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_alter_ticketcategory_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticketcategory',
            options={'verbose_name': 'Event Ticket Category', 'verbose_name_plural': 'Event Ticket Categories'},
        ),
    ]
