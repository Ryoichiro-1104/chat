# Generated by Django 3.0 on 2020-04-17 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_auto_20200416_0407'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='birthday',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('男', '男'), ('女', '女')], default='男', max_length=100),
        ),
    ]
