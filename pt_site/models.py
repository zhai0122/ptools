import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from ptools.base import BaseEntity, DownloaderCategory


# Create your models here.
# 支持的站点
class Site(BaseEntity):
    # 站点设置
    identity = models.IntegerField(verbose_name='认证ID', unique=True, help_text='唯一值，自行适配站点的请填写的尽量大')
    url = models.URLField(verbose_name='站点网址', default='', help_text='请保留网址结尾的"/"', unique=True)
    name = models.CharField(max_length=32, verbose_name='站点名称')
    nickname = models.CharField(max_length=16, verbose_name='简称', default='', help_text='英文，用于刷流')
    logo = models.URLField(verbose_name='站点logo', default='', help_text='站点logo图标')
    tracker = models.CharField(verbose_name='tracker', default='', help_text='tracker网址关键字', max_length=32)
    # 功能支持
    sign_in_support = models.BooleanField(verbose_name="签到支持", default=True)
    get_torrent_support = models.BooleanField(verbose_name="拉取种子", default=True)
    get_userinfo_support = models.BooleanField(verbose_name="站点数据", default=True)
    search_support = models.BooleanField(verbose_name="搜索支持", default=False)
    search_params = models.CharField(verbose_name='搜索参数',
                                     default='{"免费":"spstate=2","2X":"spstate=3",'
                                             '"2X免费":"spstate=4","50%":"spstate=5","2X 50%":"spstate=6",}',
                                     help_text='字典格式：{"accept":"application/json","c":"d"}',
                                     max_length=128)
    # 主要页面
    page_index = models.CharField(verbose_name='首页', default='index.php', max_length=64)
    page_default = models.CharField(verbose_name='默认搜索页面', default='torrents.php?incldead=1', max_length=64)
    page_sign_in = models.CharField(verbose_name='默认签到链接', default='attendance.php', max_length=64)
    page_control_panel = models.CharField(verbose_name='控制面板', default='usercp.php', max_length=64)
    page_detail = models.CharField(verbose_name='详情页面链接', default='details.php?id={}', max_length=64)
    page_download = models.CharField(verbose_name='默认下载链接', default='download.php?id={}', max_length=64)
    page_user = models.CharField(verbose_name='用户信息链接', default='userdetails.php?id={}', max_length=64)
    page_search = models.CharField(verbose_name='搜索链接', default='torrents.php?incldead=1&search={}', max_length=64)
    page_message = models.CharField(verbose_name='消息页面', default='messages.php', max_length=64)
    page_hr = models.CharField(verbose_name='HR考核页面', default='myhr.php?hrtype=1&userid={}', max_length=64)
    page_leeching = models.CharField(verbose_name='当前下载信息',
                                     default='getusertorrentlistajax.php?userid={}&type=leeching',
                                     max_length=64)
    page_uploaded = models.CharField(verbose_name='发布种子信息',
                                     default='getusertorrentlistajax.php?userid={}&type=uploaded',
                                     max_length=64)
    page_seeding = models.CharField(verbose_name='当前做种信息',
                                    default='getusertorrentlistajax.php?userid={}&type=seeding',
                                    max_length=64)
    page_completed = models.CharField(verbose_name='完成种子信息',
                                      default='getusertorrentlistajax.php?userid={}&type=completed',
                                      max_length=64)
    page_mybonus = models.CharField(verbose_name='魔力值页面',
                                    default='mybonus.php',
                                    max_length=64)
    page_viewfilelist = models.CharField(verbose_name='文件列表链接',
                                         default='viewfilelist.php?id={}',
                                         max_length=64)
    page_viewpeerlist = models.CharField(verbose_name='当前用户列表',
                                         default='viewpeerlist.php?id={}',
                                         max_length=64)
    sign_in_method = models.CharField(verbose_name='签到请求方法',
                                      default='get',
                                      help_text='get或post，请使用小写字母，默认get',
                                      max_length=5)
    sign_in_captcha = models.BooleanField(verbose_name='签到验证码',
                                          default=False,
                                          help_text='有签到验证码的站点请开启', )
    sign_in_params = models.CharField(verbose_name='签到请求参数',
                                      default='{}',
                                      help_text='默认无参数',
                                      max_length=128,
                                      blank=True,
                                      null=True)
    sign_in_headers = models.CharField(verbose_name='签到请求头',
                                       default='{}',
                                       help_text='字典格式：{"accept":"application/json","c":"d"},默认无参数',
                                       max_length=128)
    # HR及其他
    hr = models.BooleanField(verbose_name='H&R', default=False, help_text='站点是否开启HR')
    hr_rate = models.IntegerField(verbose_name='HR分享率', default=2, help_text='站点要求HR种子的分享率，最小：1')
    hr_time = models.IntegerField(verbose_name='HR时间', default=10, help_text='站点要求HR种子最短做种时间，单位：小时')
    sp_full = models.FloatField(verbose_name='满魔', default=100, help_text='时魔满魔')
    limit_speed = models.IntegerField(verbose_name='上传速度限制',
                                      default=100,
                                      help_text='站点盒子限速，家宽用户无需理会，单位：MB/S')
    # xpath规则
    torrents_rule = models.CharField(verbose_name='种子行信息',
                                     default='//table[@class="torrents"]/tr',
                                     max_length=128)
    name_rule = models.CharField(verbose_name='种子名称',
                                 default='.//td[@class="embedded"]/a/b/text()',
                                 max_length=128)
    title_rule = models.CharField(verbose_name='种子标题',
                                  default='.//a[contains(@href,"detail")]/parent::td/text()[last()]',
                                  max_length=128)
    detail_url_rule = models.CharField(
        verbose_name='种子详情',
        default='.//td[@class="embedded"]/a[contains(@href,"detail")]/@href',
        max_length=128)
    category_rule = models.CharField(
        verbose_name='分类',
        default='.//td[@class="rowfollow nowrap"][1]/a[1]/img/@title',
        max_length=128)
    poster_rule = models.CharField(
        verbose_name='海报',
        default='.//table/tr/td[1]/img/@src',
        max_length=128)
    magnet_url_rule = models.CharField(
        verbose_name='主页下载链接',
        default='.//td/a[contains(@href,"download.php?id=")]/@href',
        max_length=128)
    size_rule = models.CharField(verbose_name='文件大小',
                                 default='.//td[5]/text()',
                                 max_length=128)
    hr_rule = models.CharField(
        verbose_name='H&R',
        default='.//table/tr/td/img[@class="hitandrun"]/@title',
        max_length=128)
    sale_rule = models.CharField(
        verbose_name='促销信息',
        default='.//img[contains(@class,"free")]/@alt',
        max_length=128
    )
    sale_expire_rule = models.CharField(
        verbose_name='促销时间',
        default='.//img[contains(@class,"free")]/following-sibling::font/span/@title',
        max_length=128)
    release_rule = models.CharField(
        verbose_name='发布时间',
        default='.//td[4]/span/@title',
        max_length=128)
    seeders_rule = models.CharField(
        verbose_name='做种人数',
        default='.//a[contains(@href,"#seeders")]/text()',
        max_length=128)
    leechers_rule = models.CharField(
        verbose_name='下载人数',
        default='.//a[contains(@href,"#leechers")]/text()',
        max_length=128)
    completers_rule = models.CharField(
        verbose_name='完成人数',
        default='.//a[contains(@href,"viewsnatches")]//text()',
        max_length=128)
    detail_title_rule = models.CharField(
        verbose_name='详情页种子标题',
        default='//h1/text()[1]',
        max_length=128)
    detail_subtitle_rule = models.CharField(
        verbose_name='详情页种子副标题',
        default='//td[contains(text(),"副标题")]/following-sibling::td/text()[1]',
        max_length=128)
    detail_download_url_rule = models.CharField(
        verbose_name='详情页种子链接',
        default='//a[@class="index" and contains(@href,"download.php")]/@href',
        max_length=128)
    detail_size_rule = models.CharField(
        verbose_name='详情页种子大小',
        default='//td//b[contains(text(),"大小")]/following::text()[1]',
        max_length=128)
    detail_category_rule = models.CharField(
        verbose_name='详情页种子类型',
        default='//td/b[contains(text(),"类型")]/following-sibling::text()[1]',
        max_length=128)
    detail_area_rule = models.CharField(
        verbose_name='详情页种子地区',
        default='//h1/following::td/b[contains(text(),"地区")]/text()',
        max_length=128)
    detail_count_files_rule = models.CharField(
        verbose_name='详情页文件数',
        default='//td/b[contains(text(),"文件数")]/following-sibling::text()[1]',
        max_length=128)
    # HASH RULE
    detail_hash_rule = models.CharField(
        verbose_name='详情页种子HASH',
        default='//td/b[contains(text(),"Hash")]/following-sibling::text()[1]',
        max_length=128)
    detail_free_rule = models.CharField(
        verbose_name='详情页促销标记',
        default='//td//b[contains(text(),"大小")]/following::text()[1]',
        max_length=128)
    detail_free_expire_rule = models.CharField(
        verbose_name='详情页促销时间',
        default='//h1/b/font[contains(@class,"free")]/parent::b/following-sibling::b/span/@title',
        max_length=128)
    detail_douban_rule = models.CharField(
        verbose_name='详情页豆瓣信息',
        help_text='提取做种列表中文件大小计算总量',
        default='//td/a[starts-with(@href,"https://movie.douban.com/subject/")][1]',
        max_length=128)
    detail_year_publish_rule = models.CharField(
        verbose_name='详情页豆瓣信息',
        help_text='提取做种列表中文件大小计算总量',
        default='year_current_publish: //td/b[contains(text(),"发行版年份")]/text()',
        max_length=128)

    remark = models.TextField(verbose_name='备注', default='', null=True, blank=True)
    # 状态信息XPath
    invitation_rule = models.CharField(
        verbose_name='邀请资格',
        default='//span/a[contains(@href,"invite.php?id=")]/following-sibling::text()[1]',
        max_length=128)
    time_join_rule = models.CharField(
        verbose_name='注册时间',
        default='//td[contains(text(),"加入")]/following-sibling::td/span/@title',
        max_length=128)
    latest_active_rule = models.CharField(
        verbose_name='最后活动时间',
        default='//td[contains(text(),"最近动向")]/following-sibling::td/span/@title',
        max_length=128)
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
    my_sp_rule = models.CharField(
        verbose_name='魔力值',
        default='//a[@href="mybonus.php"]/following-sibling::text()[1]',
        max_length=128)
    hour_sp_rule = models.CharField(
        verbose_name='时魔',
        default='//div[contains(text(),"每小时能获取")]/text()[1]',
        max_length=128)
    my_bonus_rule = models.CharField(
        verbose_name='保种积分',
        default='//font[@class="color_bonus" and contains(text(),"积分")]/following-sibling::text()[1]',
        max_length=128)
    my_level_rule = models.CharField(
        verbose_name='用户等级',
        default='//table[@id="info_block"]//span/a[contains(@class,"_Name") and contains(@href,"userdetails.php?id=")]/@class',
        max_length=128
    )
    my_passkey_rule = models.CharField(
        verbose_name='Passkey',
        default='//td[contains(text(),"密钥")]/following-sibling::td[1]/text()',
        max_length=128
    )
    my_uid_rule = models.CharField(
        verbose_name='用户ID',
        default='//table[@id="info_block"]//span/a[contains(@class,"_Name") and contains(@href,"userdetails.php?id=")]/@href',
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

    publish_rule = models.CharField(verbose_name='发种数量',
                                    default='//p/preceding-sibling::b/text()[1]',
                                    max_length=128)

    seed_rule = models.CharField(verbose_name='做种数量',
                                 default='//img[@class="arrowup"]/following-sibling::text()[1]',
                                 max_length=128)

    seed_vol_rule = models.CharField(verbose_name='做种大小',
                                     default='//tr/td[3]',
                                     help_text='需对数据做处理',
                                     max_length=128)
    mailbox_rule = models.CharField(verbose_name='邮件规则',
                                    default='//a[@href="messages.php"]/font[contains(text(),"条")]/text()[1]',
                                    help_text='获取新邮件',
                                    max_length=128)
    message_title = models.CharField(verbose_name='邮件标题',
                                     default='//img[@alt="Unread"]/parent::td/following-sibling::td/a[1]//text()',
                                     help_text='获取邮件标题',
                                     max_length=128)
    notice_rule = models.CharField(verbose_name='公告规则',
                                   default='//a[@href="index.php"]/font[contains(text(),"条")]/text()[1]',
                                   help_text='获取新公告',
                                   max_length=128)
    notice_title = models.CharField(verbose_name='公告标题',
                                    default='//td[@class="text"]/div/a//text()',
                                    help_text='获取公告标题',
                                    max_length=128)
    notice_content = models.CharField(verbose_name='公告内容',
                                      default='//td[@class="text"]/div/a/following-sibling::div',
                                      help_text='获取公告内容',
                                      max_length=128)
    full_site_free = models.CharField(verbose_name='站免规则',
                                      default='//td/b/a/font[contains(text(),"全站") and contains(text(),"Free")]/text()',
                                      help_text='站免信息',
                                      max_length=128)

    class Meta:
        verbose_name = '站点信息'
        verbose_name_plural = verbose_name
        ordering = ['name', ]

    def __str__(self):
        return self.name


class UserLevelRule(BaseEntity):
    site = models.ForeignKey(verbose_name='站 点', to=Site, to_field='identity', on_delete=models.CASCADE)
    level_id = models.IntegerField(verbose_name='等级id', default=1)
    level = models.CharField(verbose_name='等 级', default='User', max_length=24, help_text='请去除空格')
    days = models.IntegerField(verbose_name='时 间', default=0, help_text='原样输入，单位：周')
    uploaded = models.CharField(verbose_name='上 传', default=0, help_text='原样输入，例：50GB，1.5TB', max_length=12)
    downloaded = models.CharField(verbose_name='下 载', default=0, help_text='原样输入，例：50GB，1.5TB', max_length=12)
    bonus = models.FloatField(verbose_name='魔 力', default=0)
    score = models.IntegerField(verbose_name='积 分', default=0)
    ratio = models.FloatField(verbose_name='分享率', default=0)
    torrents = models.IntegerField(verbose_name='发 种', help_text='发布种子数', default=0)
    leeches = models.IntegerField(verbose_name='吸血数', help_text='完成种子数', default=0)
    seeding_delta = models.FloatField(verbose_name='做种时间', help_text='累计做种时间', default=0)
    rights = models.TextField(verbose_name='权 利', max_length=256,
                              help_text='当前等级所享有的权利与义务')

    def __str__(self):
        return f'{self.site.nickname}/{self.level}'

    class Meta:
        unique_together = ('site', 'level_id', 'level',)
        verbose_name = '升级进度'
        verbose_name_plural = verbose_name


class MySite(BaseEntity):
    site = models.OneToOneField(verbose_name='站点', to=Site, on_delete=models.CASCADE)
    sort_id = models.IntegerField(verbose_name='排序', default=1)
    # 用户信息
    user_id = models.CharField(verbose_name='用户ID', max_length=16,
                               help_text='请填写<font color="orangered">数字UID</font>，'
                                         '<font color="orange">* az,cz,ez,莫妮卡、普斯特请填写用户名</font>')
    passkey = models.CharField(max_length=128, verbose_name='PassKey', blank=True, null=True)
    cookie = models.TextField(verbose_name='COOKIE', help_text='与UA搭配使用效果更佳，请和UA在同一浏览器提取')
    expires = models.DateTimeField(verbose_name='COOKIE有效期', help_text='COOKIE有效期',
                                   default=datetime.datetime.strptime('2023-01-01 12:30:00', '%Y-%m-%d %H:%M:%S'))
    user_agent = models.TextField(verbose_name='User-Agent', help_text='请填写你获取cookie的浏览器的User-Agent',
                                  default='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                                          '(KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42')
    # 用户设置
    hr = models.BooleanField(verbose_name='开启HR下载', default=False, help_text='是否下载HR种子')
    sign_in = models.BooleanField(verbose_name='开启签到', default=True, help_text='是否开启签到')
    get_info = models.BooleanField(verbose_name='抓取信息', default=True, help_text='是否抓取站点数据')
    search = models.BooleanField(verbose_name='开启搜索', default=True, help_text='是否开启搜索')
    # 用户数据 自动拉取
    # invitation = models.IntegerField(verbose_name='邀请资格', default=0)
    time_join = models.DateTimeField(verbose_name='注册时间', blank=True, null=True, help_text='请务必填写此项！')
    latest_active = models.DateTimeField(verbose_name='最近活动时间', blank=True, null=True)
    # sp_hour = models.FloatField(verbose_name='时魔', default=0)
    my_level = models.CharField(verbose_name='用户等级', max_length=16, default='')
    my_hr = models.CharField(verbose_name='H&R', max_length=16, default='')
    # leech = models.IntegerField(verbose_name='当前下载', default=0)
    # seed = models.IntegerField(verbose_name='当前做种', default=0)
    mail = models.IntegerField(verbose_name='新邮件', default=0)

    # publish = models.IntegerField(verbose_name='发布种子', default=0)

    def __str__(self):
        return self.site.name

    class Meta:
        verbose_name = '我的站点'
        verbose_name_plural = verbose_name


# 站点信息
class SiteStatus(BaseEntity):
    # 获取日期，只保留当天最新数据
    site = models.ForeignKey(verbose_name='站点名称', to=MySite, on_delete=models.CASCADE)
    # 签到，有签到功能的访问签到页面，无签到的访问个人主页
    uploaded = models.IntegerField(verbose_name='上传量', default=0)
    downloaded = models.IntegerField(verbose_name='下载量', default=0)
    ratio = models.FloatField(verbose_name='分享率', default=0)
    my_sp = models.FloatField(verbose_name='魔力值', default=0)
    my_bonus = models.FloatField(verbose_name='做种积分', default=0)
    seed_vol = models.IntegerField(verbose_name='做种体积', default=0)
    leech = models.IntegerField(verbose_name='当前下载', default=0)
    seed = models.IntegerField(verbose_name='当前做种', default=0)
    sp_hour = models.FloatField(verbose_name='时魔', default=0)
    publish = models.IntegerField(verbose_name='发布种子', default=0)
    invitation = models.IntegerField(verbose_name='邀请资格', default=0)

    class Meta:
        verbose_name = '我的数据'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.site.site.name


class SignIn(BaseEntity):
    site = models.ForeignKey(verbose_name='站点名称', to=MySite, on_delete=models.CASCADE)
    sign_in_today = models.BooleanField(verbose_name='签到', default=False)
    sign_in_info = models.CharField(verbose_name='信息', default='', max_length=256)

    class Meta:
        verbose_name = '签到'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.site.site.name


class Downloader(BaseEntity):
    # 下载器名称
    name = models.CharField(max_length=12, verbose_name='名称')
    # 下载器类别             tr  qb  de
    category = models.CharField(max_length=128, choices=DownloaderCategory.choices,
                                default=DownloaderCategory.qBittorrent,
                                verbose_name='下载器')
    # 用户名
    username = models.CharField(max_length=16, verbose_name='用户名')
    # 密码
    password = models.CharField(max_length=128, verbose_name='密码')
    # host
    host = models.CharField(max_length=32, verbose_name='HOST')
    # port
    port = models.IntegerField(default=8999, verbose_name='端口', validators=[
        MaxValueValidator(65535),
        MinValueValidator(1001)
    ])
    # 预留空间
    reserved_space = models.IntegerField(default=30, verbose_name='预留磁盘空间', validators=[
        MinValueValidator(1),
        MaxValueValidator(512)
    ], help_text='单位GB，最小为1G，最大512G')

    class Meta:
        verbose_name = '下载器'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 种子信息
class TorrentInfo(BaseEntity):
    site = models.ForeignKey(to=Site, on_delete=models.CASCADE, verbose_name='所属站点', null=True)
    name = models.CharField(max_length=256, verbose_name='种子名称', default='')
    title = models.CharField(max_length=256, verbose_name='标题', default='')
    category = models.CharField(max_length=128, verbose_name='分类', default='')
    poster_url = models.URLField(max_length=512, verbose_name='海报链接', default='')
    detail_url = models.URLField(max_length=512, verbose_name='种子详情', default='')
    magnet_url = models.URLField(verbose_name='下载链接')
    download_url = models.URLField(verbose_name='种子链接', unique=True, max_length=255)
    size = models.IntegerField(verbose_name='文件大小', default=0)
    state = models.BooleanField(max_length=16, verbose_name='推送状态', default=False)
    save_path = models.FilePathField(verbose_name='保存路径', default='/downloads/brush')
    hr = models.BooleanField(verbose_name='H&R考核', default=True, help_text='绿色为通过或无需HR考核')
    sale_status = models.CharField(verbose_name='优惠状态', default='无促销', max_length=16)
    sale_expire = models.CharField(verbose_name='到期时间', default='无限期', max_length=32)
    on_release = models.CharField(verbose_name='发布时间', default='', max_length=32)
    seeders = models.CharField(verbose_name='做种人数', default='0', max_length=8)
    leechers = models.CharField(verbose_name='下载人数', default='0', max_length=8)
    completers = models.CharField(verbose_name='完成人数', default='0', max_length=8)
    downloader = models.ForeignKey(to=Downloader,
                                   on_delete=models.CASCADE,
                                   verbose_name='下载器',
                                   blank=True, null=True)
    hash_string = models.CharField(max_length=128, verbose_name='Info_hash', default='')
    viewfilelist = models.CharField(max_length=128, verbose_name='文件列表', default='')
    viewpeerlist = models.FloatField(max_length=128, verbose_name='下载总进度', default=0)
    peer_list_speed = models.FloatField(max_length=128, verbose_name='平均上传速度', default=0)

    class Meta:
        verbose_name = '种子管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
