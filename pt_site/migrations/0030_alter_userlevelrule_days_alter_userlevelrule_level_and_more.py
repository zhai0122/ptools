# Generated by Django 4.1.2 on 2023-01-07 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_site', '0029_alter_userlevelrule_downloaded_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlevelrule',
            name='days',
            field=models.IntegerField(default=0, help_text='原样输入，单位：周', verbose_name='时 间'),
        ),
        migrations.AlterField(
            model_name='userlevelrule',
            name='level',
            field=models.CharField(default='User', help_text='请去除空格', max_length=24, verbose_name='等 级'),
        ),
        migrations.AlterField(
            model_name='userlevelrule',
            name='rights',
            field=models.TextField(help_text='当前等级所享有的权利与义务', max_length=256, verbose_name='权 利'),
        ),
    ]
