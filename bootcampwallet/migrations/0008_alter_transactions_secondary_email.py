# Generated by Django 3.2 on 2021-11-12 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bootcampwallet', '0007_auto_20211112_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='secondary_email',
            field=models.EmailField(max_length=254, null=True, verbose_name='secondary_email'),
        ),
    ]
