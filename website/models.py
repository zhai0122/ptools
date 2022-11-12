import django
from django.db import models

from ptools.base import BaseEntity, Schemas


# Create your models here.

class WebSite(BaseEntity):
    """站点基础信息"""
    # 基本信息
    url = models.URLField(verbose_name='站点网址', default='', help_text='请保留网址结尾的"/"', unique=True)
    name = models.CharField(max_length=32, verbose_name='站点名称', help_text='站点常用名称')
    nickname = models.CharField(max_length=32, verbose_name='别称', help_text='昵称，小名', default='')
    schemas = models.CharField(choices=Schemas.choices, default=Schemas.NexusPHP, verbose_name='站点架构',
                               max_length=16)
    logo = models.URLField(verbose_name='站点logo', default='', help_text='站点logo图标')
    tracker = models.CharField(verbose_name='tracker', default='', help_text='tracker网址关键字', max_length=32)
    tags = models.CharField(verbose_name='标签', help_text='定义站点资源标签，使用英文逗号‘,’分割', default='',
                            max_length=128)
    hr = models.BooleanField(verbose_name='H&R', help_text='站点HR状态', default=False)
    # 功能支持
    sign_in = models.BooleanField(verbose_name='签到', help_text='是否需要签到', default=False)
    info_capture = models.BooleanField(verbose_name='抓取信息', default=True, help_text='是否支持抓取信息')
    torrent_capture = models.BooleanField(verbose_name='抓取种子', default=True, help_text='是否支持抓取种子')
    auto_login = models.BooleanField(verbose_name='自动登录', default=False, help_text='是否支持自动登录并获取Cookie')
    search = models.BooleanField(verbose_name='聚合搜索', default=True, help_text='是否支持聚合搜索')
    assist = models.BooleanField(verbose_name='辅种', default=True, help_text='是否支持辅种')
    exam = models.BooleanField(verbose_name='新手考核', default=True, help_text='是否支持新手考核信息比对')
    invite = models.BooleanField(verbose_name='邀请', default=True, help_text='是否支持邀请')

    class Meta:
        verbose_name = 'PT站点'
        verbose_name_plural = verbose_name
        ordering = ['name', ]

    def __str__(self):
        return self.name


class OwnSite(BaseEntity):
    """我的站点，保存UID，PASSKEY，Cookie"""
    site = models.OneToOneField(verbose_name='站点', to=WebSite, on_delete=models.CASCADE)
    sort_id = models.IntegerField(verbose_name='排序', default=99)
    # 用户信息
    user_id = models.CharField(verbose_name='用户ID', max_length=16)
    passkey = models.CharField(max_length=128, verbose_name='Passkey', blank=True, null=True)
    cookie = models.TextField(verbose_name='Cookie')
    user_agent = models.CharField(
        verbose_name='User-Agent', max_length=256,
        default='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.28',
    )
    # 功能开启
    hr = models.BooleanField(verbose_name='开启HR下载', default=False, help_text='是否下载HR种子')
    sign_in = models.BooleanField(verbose_name='开启签到', default=True, help_text='是否开启签到')
    search = models.BooleanField(verbose_name='开启搜索', default=True, help_text='是否开启搜索')

    class Meta:
        verbose_name = '我的站点'
        verbose_name_plural = verbose_name
        ordering = ['sort_id', ]

    def __str__(self):
        return self.site


class SignIn(BaseEntity):
    """
    签到代码，
    签到调用的代码模板
    """
    site = models.OneToOneField(verbose_name='站点', to=WebSite, on_delete=models.CASCADE)
    url_check = models.CharField(max_length=128, verbose_name='签到检测链接', default='attendance.php')
    url_sign_in = models.CharField(max_length=128, verbose_name='签到链接', default='attendance.php')
    params_sign = models.CharField(max_length=1024, verbose_name='签到参数', default='')
    params_name_xpath = models.CharField(
        max_length=1024, verbose_name='签到参数名称', default='', help_text='支持多个参数，使用英文逗号‘,’分割'
    )
    params_value_xpath = models.CharField(
        max_length=1024, verbose_name='签到参数Value', default='',
        help_text='支持多个参数，使用英文逗号‘,’分割'
    )
    method_sign = models.CharField(max_length=8, verbose_name='请求方式', choices=(
        ('post', 'post'),
        ('get', 'get')
    ), default='get')
    res_sign_xpath = models.CharField(max_length=1024, verbose_name='签到信息Xpath', default='')

    class Meta:
        verbose_name = '站点签到'
        verbose_name_plural = verbose_name
        ordering = ['site', ]

    def __str__(self):
        return self.site


class AutoLogin(BaseEntity):
    """自动登录"""
    site = models.OneToOneField(verbose_name='站点', to=WebSite, on_delete=models.CASCADE)
    username = models.CharField(max_length=32, verbose_name='用户名')
    password = models.CharField(max_length=32, verbose_name='密码')
    captcha = models.CharField(max_length=16, verbose_name='验证码字段名')
    captcha_xpath = models.CharField(max_length=256, verbose_name='验证码Xpath')

    class Meta:
        verbose_name = '自动登录'
        verbose_name_plural = verbose_name
        ordering = ['site', ]

    def __str__(self):
        return self.site


class InfoXpath(BaseEntity):
    """获取个人信息Xpath规则模板"""
    site = models.OneToOneField(verbose_name='站点', to=WebSite, on_delete=models.CASCADE)
    url_user = models.CharField(verbose_name='个人主页', default='userdetails.php?id={}', max_length=64)
    url_bonus = models.CharField(verbose_name='魔力值页面',
                                 default='mybonus.php',
                                 max_length=64)
    url_seeding = models.CharField(verbose_name='当前做种信息',
                                   default='getusertorrentlistajax.php?userid={}&type=seeding',
                                   max_length=64)
    uploaded_rule = models.CharField(
        verbose_name='上传量',
        default='//font[@class="color_uploaded"]/following-sibling::text()[1]',
        max_length=128)
    downloaded_rule = models.CharField(
        verbose_name='下载量',
        default='//font[@class="color_downloaded"]/following-sibling::text()[1]',
        max_length=128)
    ratio_rule = models.CharField(
        verbose_name='分享率',
        default='//font[@class="color_ratio"][1]/following-sibling::text()[1]',
        max_length=128)
    my_bonus_rule = models.CharField(
        verbose_name='魔力值',
        default='//a[@href="mybonus.php"]/following-sibling::text()[1]',
        max_length=128)
    hour_bonus_rule = models.CharField(
        verbose_name='时魔',
        default='//div[contains(text(),"每小时能获取")]/text()[1]',
        max_length=128)
    my_score_rule = models.CharField(
        verbose_name='保种积分',
        default='//font[@class="color_bonus" and contains(text(),"积分")]/following-sibling::text()[1]',
        max_length=128)
    my_level_rule = models.CharField(
        verbose_name='用户等级',
        default='//table[@id="info_block"]//span/a[contains(@class,"_Name") and contains(@href,"userdetails.php?id=")]/@class',
        max_length=128
    )
    my_hr_rule = models.CharField(
        verbose_name='H&R',
        default='//a[@href="myhr.php"]//text()',
        max_length=128)
    leech_rule = models.CharField(
        verbose_name='下载数量',
        default='//img[@class="arrowdown"]/following-sibling::text()[1]',
        max_length=128)

    seed_rule = models.CharField(verbose_name='做种数量',
                                 default='//img[@class="arrowup"]/following-sibling::text()[1]',
                                 max_length=128)

    my_invite_rule = models.CharField(
        verbose_name='邀请资格',
        default='//span/a[contains(@href,"invite.php?id=")]/following-sibling::text()[1]',
        max_length=128)

    seed_vol_rule = models.CharField(verbose_name='做种大小',
                                     default='//tr/td[3]',
                                     help_text='需对数据做处理',
                                     max_length=128)
    mailbox_rule = models.CharField(verbose_name='邮件规则',
                                    default='//a[@href="messages.php"]/font[contains(text(),"条")]/text()[1]',
                                    help_text='获取新邮件',
                                    max_length=128)
    notice_rule = models.CharField(verbose_name='公告规则',
                                   default='//a[@href="index.php"]/font[contains(text(),"条")]/text()[1]',
                                   help_text='获取新公告',
                                   max_length=128)
    time_join_rule = models.CharField(
        verbose_name='注册时间',
        default='//td[contains(text(),"加入")]/following-sibling::td/span/@title',
        max_length=128)
    latest_active_rule = models.CharField(
        verbose_name='最后活动时间',
        default='//td[contains(text(),"最近动向")]/following-sibling::td/span/@title',
        max_length=128)

    class Meta:
        verbose_name = '个人信息规则'
        verbose_name_plural = verbose_name
        ordering = ['site', ]

    def __str__(self):
        return self.site


class HRListXpath(BaseEntity):
    """种子列表Xpath模板"""
    site = models.OneToOneField(verbose_name='站点', to=WebSite, on_delete=models.CASCADE)
    url_hr = models.CharField(verbose_name='HR考核信息',
                              default='myhr.php?status=1',
                              max_length=64)
    torrents = models.CharField(verbose_name='考核种子列表',
                                default='//table[@id="hr-table"]/tbody/tr',
                                max_length=64)
    torrent_name = models.CharField(verbose_name='考核种子名称',
                                    default='./td[2]//text()',
                                    max_length=64)
    torrent_url = models.CharField(verbose_name='种子链接',
                                   default='./td[2]//a/@href',
                                   max_length=64)
    torrent_ratio = models.CharField(verbose_name='种子分享率',
                                     default='./td[2]//a/@href',
                                     max_length=64)
    time_to_seeding = models.CharField(verbose_name='还需做种时间',
                                       default='./td[6]//text()',
                                       max_length=64)
    time_end_seeding = models.CharField(verbose_name='剩余考核时间',
                                        default='./td[6]//text()',
                                        max_length=64)
    """
    <table width="100%" id="hr-table">
        <tbody>
            <tr>
                <td class="colhead" align="center"> H&amp;R ID</td>
                <td class="colhead" align="center"> 种子名称</td>
                <td class="colhead" align="center">上传量</td>
                <td class="colhead" align="center">下载量</td>
                <td class="colhead" align="center">分享率</td>
                <td class="colhead" align="center">还需做种时间</td>
                <td class="colhead" align="center">下载完成时间</td>
                <td class="colhead" align="center">剩余考察时间</td>
                <td class="colhead" align="center">备注</td>
                <td class="colhead" align="center">操作</td>
            </tr>
        </tbody>
    </table>
    """

    class Meta:
        verbose_name = 'H&R规则'
        verbose_name_plural = verbose_name
        ordering = ['site', ]

    def __str__(self):
        return self.site


class TorrentListXpath(BaseEntity):
    """种子列表Xpath模板"""
    site = models.OneToOneField(verbose_name='站点', to=WebSite, on_delete=models.CASCADE)

    pass


class Examine(BaseEntity):
    """新手考核"""
    site = models.OneToOneField(verbose_name='站点', to=WebSite, on_delete=models.CASCADE)
    end_time = models.DateTimeField(verbose_name='考核结束时间', default=django.utils.timezone.now)
    bonus = models.FloatField(verbose_name='魔力值', default=0)
    score = models.FloatField(verbose_name='做种积分', default=0)
    uploaded = models.FloatField(verbose_name='上传量', default=50, help_text='计算单位：GB')
    downloaded = models.FloatField(verbose_name='魔力值', default=50, help_text='计算单位：GB')
    avg_seed_time = models.FloatField(verbose_name='平均做种时间', default=0, help_text='计算单位：小时')
    rate = models.FloatField(verbose_name='做种率', default=0)

    class Meta:
        verbose_name = '新手考核'
        verbose_name_plural = verbose_name
        ordering = ['site', ]

    def __str__(self):
        return self.site
