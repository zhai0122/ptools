# Generated by Django 4.1.2 on 2023-01-05 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_site', '0026_alter_userlevelrule_options_alter_userlevelrule_days_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='notice_title',
            field=models.CharField(default='//td[@class="text"]/div/a//text()', help_text='获取公告标题', max_length=128, verbose_name='公告标题'),
        ),
        migrations.AlterField(
            model_name='site',
            name='message_title',
            field=models.CharField(default='//img[@alt="Unread"]/parent::td/following-sibling::td/a[1]//text()', help_text='获取邮件标题', max_length=128, verbose_name='邮件标题'),
        ),
        migrations.DeleteModel(
            name='UserLevelRule',
        ),
    ]