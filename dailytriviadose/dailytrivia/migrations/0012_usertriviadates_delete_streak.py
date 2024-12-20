# Generated by Django 5.0.6 on 2024-11-11 18:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dailytrivia', '0011_streak'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTriviaDates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('play_dates', models.JSONField(default=list)),
                ('trivia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dailytrivia.trivia')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Streak',
        ),
    ]
