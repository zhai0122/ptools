# Generated by Django 4.1.2 on 2023-01-05 11:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pt_site', '0027_site_notice_title_alter_site_message_title_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLevelRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('level_id', models.IntegerField(default=1, verbose_name='等级id')),
                ('level', models.CharField(default='User', max_length=24, verbose_name='等 级')),
                ('days', models.IntegerField(default=0, help_text='单位：天', verbose_name='时 间')),
                ('uploaded', models.IntegerField(default=0, help_text='单位：GB', verbose_name='上 传')),
                ('downloaded', models.IntegerField(default=0, help_text='单位：GB', verbose_name='下 载')),
                ('bonus', models.IntegerField(default=0, verbose_name='魔 力')),
                ('score', models.IntegerField(default=0, verbose_name='积 分')),
                ('ratio', models.FloatField(default=0, verbose_name='分享率')),
                ('torrents', models.IntegerField(default=0, verbose_name='发 种')),
                ('rights', models.CharField(help_text='当前等级所享有的权利与义务', max_length=128, verbose_name='权 利')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pt_site.site', verbose_name='站 点')),
            ],
            options={
                'verbose_name': '升级进度',
                'verbose_name_plural': '升级进度',
                'unique_together': {('site', 'level_id', 'level')},
            },
        ),
    ]