# Generated by Django 5.0.6 on 2024-12-04 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dailytrivia', '0014_remove_usertriviadates_highest_streak'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='timezone',
            field=models.CharField(default='UTC', max_length=50),
        ),
    ]
