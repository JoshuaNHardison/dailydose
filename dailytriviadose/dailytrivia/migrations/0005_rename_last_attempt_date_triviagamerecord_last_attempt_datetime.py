# Generated by Django 5.0.6 on 2024-11-06 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dailytrivia', '0004_alter_trivia_reset_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='triviagamerecord',
            old_name='last_attempt_date',
            new_name='last_attempt_datetime',
        ),
    ]