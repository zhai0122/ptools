# Generated by Django 4.1.2 on 2023-01-19 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pt_site", "0037_alter_site_nickname"),
    ]

    operations = [
        migrations.RemoveField(model_name="mysite", name="invitation",),
        migrations.RemoveField(model_name="mysite", name="leech",),
        migrations.RemoveField(model_name="mysite", name="publish",),
        migrations.RemoveField(model_name="mysite", name="seed",),
        migrations.RemoveField(model_name="mysite", name="sp_hour",),
        migrations.AddField(
            model_name="mysite",
            name="get_info",
            field=models.BooleanField(
                default=True, help_text="是否抓取站点数据", verbose_name="抓取信息"
            ),
        ),
        migrations.AddField(
            model_name="sitestatus",
            name="invitation",
            field=models.IntegerField(default=0, verbose_name="邀请资格"),
        ),
        migrations.AddField(
            model_name="sitestatus",
            name="leech",
            field=models.IntegerField(default=0, verbose_name="当前下载"),
        ),
        migrations.AddField(
            model_name="sitestatus",
            name="publish",
            field=models.IntegerField(default=0, verbose_name="发布种子"),
        ),
        migrations.AddField(
            model_name="sitestatus",
            name="seed",
            field=models.IntegerField(default=0, verbose_name="当前做种"),
        ),
        migrations.AddField(
            model_name="sitestatus",
            name="sp_hour",
            field=models.FloatField(default=0, verbose_name="时魔"),
        ),
    ]