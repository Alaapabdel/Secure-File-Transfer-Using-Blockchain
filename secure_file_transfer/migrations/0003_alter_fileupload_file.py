# Generated by Django 5.0.3 on 2024-06-06 08:47

import secure_file_transfer.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secure_file_transfer', '0002_fileupload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='file',
            field=models.FileField(storage=secure_file_transfer.storage.OverwriteStorage(), upload_to='uploads/'),
        ),
    ]
