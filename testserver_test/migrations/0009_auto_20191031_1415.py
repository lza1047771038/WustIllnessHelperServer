# Generated by Django 2.2.5 on 2019-10-31 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testserver_test', '0008_auto_20191031_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadimage',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
