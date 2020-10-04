# Generated by Django 2.2 on 2020-10-04 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instagram', '0005_auto_20201004_1523'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instagram_Apı_Constants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ig_sig_key', models.CharField(default='19ce5f445dbfd9d29c59dc2a78c616a7fc090a8e018b9267bc4240a30244c53b', max_length=300, verbose_name='IG signature key')),
                ('ig_capabilites', models.CharField(default='3brTvw==', max_length=300, verbose_name='IG capabilites')),
                ('sig_key_version', models.CharField(default='4', max_length=100, verbose_name='Signature key version')),
                ('app_version', models.CharField(default='76.0.0.15.395', max_length=100, verbose_name='App version')),
                ('application_id', models.CharField(default='567067343352427', max_length=200, verbose_name='Application id')),
                ('fb_http_engine', models.CharField(default='Liger', max_length=200, verbose_name='Fb http engine')),
                ('android_version', models.IntegerField(default=24, max_length=200, verbose_name='Android version')),
                ('android_relase', models.CharField(default='7.0', max_length=200, verbose_name='Android relase')),
                ('phone_manufacturer', models.CharField(default='samsung', max_length=200, verbose_name='Phone Manufacturer')),
                ('phone_device', models.CharField(default='SM-G930F', max_length=200, verbose_name='Phone Device')),
                ('phone_model', models.CharField(default='herolte', max_length=200, verbose_name='Phone Model')),
                ('phone_dpi', models.CharField(default='640dpi', max_length=200, verbose_name='Phone DPI')),
                ('phone_resolution', models.CharField(default='1440x2560', max_length=200, verbose_name='Phone Resolution')),
                ('phone_chipset', models.CharField(default='samsungexynos8890', max_length=200, verbose_name='Phone Chipset')),
                ('version_code', models.CharField(default='138226743', max_length=200, verbose_name='Version code')),
            ],
        ),
        migrations.AddField(
            model_name='socinstaproxy',
            name='location',
            field=models.CharField(default='Amsterdam', max_length=200, verbose_name='Location'),
        ),
        migrations.AddField(
            model_name='socinstaproxy',
            name='port',
            field=models.CharField(default='3128', max_length=200, verbose_name='Port'),
        ),
    ]
