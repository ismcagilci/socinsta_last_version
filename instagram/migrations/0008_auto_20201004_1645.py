# Generated by Django 2.2 on 2020-10-04 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instagram', '0007_auto_20201004_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socinstaproxy',
            name='password',
            field=models.CharField(max_length=200, null=True, verbose_name='proxy passoword'),
        ),
        migrations.AlterField(
            model_name='socinstaproxy',
            name='port',
            field=models.CharField(max_length=200, null=True, verbose_name='Port'),
        ),
        migrations.AlterField(
            model_name='socinstaproxy',
            name='username',
            field=models.CharField(max_length=200, null=True, verbose_name='proxy username'),
        ),
    ]
