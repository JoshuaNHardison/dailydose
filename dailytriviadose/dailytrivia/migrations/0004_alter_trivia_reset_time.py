# Generated by Django 5.0.6 on 2024-11-05 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dailytrivia', '0003_trivia_reset_time_triviagamerecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trivia',
            name='reset_time',
            field=models.TimeField(),
        ),
    ]
