# Generated by Django 5.0.6 on 2024-11-11 17:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dailytrivia', '0010_remove_triviagamerecord_streak_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='Streak',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('play_date', models.DateField()),
                ('trivia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dailytrivia.trivia')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
