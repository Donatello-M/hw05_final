# Generated by Django 2.2.9 on 2021-04-07 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_group_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(default=None, max_length=14, unique=True),
        ),
    ]
