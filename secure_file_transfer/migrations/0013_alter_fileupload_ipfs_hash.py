# Generated by Django 5.0.6 on 2024-06-08 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secure_file_transfer', '0012_alter_fileupload_ipfs_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='ipfs_hash',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
