# Generated by Django 5.1.4 on 2025-01-18 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]
