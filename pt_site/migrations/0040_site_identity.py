# Generated by Django 4.1.2 on 2023-01-30 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pt_site", "0039_site_publish_rule"),
    ]

    operations = [
        migrations.AddField(
            model_name="site",
            name="identity",
            field=models.IntegerField(
                help_text="唯一值，自行适配站点的请填写的尽量大", null=True, verbose_name="认证ID"
            ),
        ),
    ]
