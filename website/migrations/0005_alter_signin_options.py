# Generated by Django 4.1 on 2022-11-03 22:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0004_alter_ownsite_options_ownsite_user_agent_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="signin",
            options={
                "ordering": ["site"],
                "verbose_name": "站点签到",
                "verbose_name_plural": "站点签到",
            },
        ),
    ]
