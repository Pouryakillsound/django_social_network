# Generated by Django 4.2.2 on 2023-07-18 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_profile_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='age',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]