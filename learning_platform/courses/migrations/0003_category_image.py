# Generated by Django 4.2.14 on 2024-08-04 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_category_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='category_images/'),
        ),
    ]
