# Generated by Django 2.2.5 on 2019-10-31 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testserver_test', '0007_survey_problemoffset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadimage',
            name='id',
            field=models.IntegerField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]