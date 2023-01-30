import time
import traceback
from datetime import datetime

import qbittorrentapi
import transmission_rpc
from django.contrib import admin, messages
from django.http import JsonResponse
from django.utils.html import format_html
from django_admin_inline_paginator.admin import TabularInlinePaginated
from simpleui.admin import AjaxAdmin
from transmission_rpc import Torrent

from pt_site.UtilityTool import MessageTemplate, FileSizeConvert
from pt_site.models import Site, Downloader, SignIn, UserLevelRule
from pt_site.models import TorrentInfo, SiteStatus, MySite
# Register your models here.
from pt_site.views import pool, pt_spider
from ptools.base import StatusCodeEnum, DownloaderCategory

admin.site.site_header = 'PT一下，你就晓嘚'
admin.site.site_title = 'PT一下，你就晓嘚'
admin.site.index_title = '我在后台首页'


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):  # instead of ModelAdmin
    # 显示字段
    list_display = (
        'name',
        'custom_url',
        'sign_in_support',
        'get_userinfo_support',
        'get_torrent_support',
        'search_support',
        'created_at',
        'updated_at',
        # 'remark',

    )
    actions_selection_counter = True
    # list_display_links = None

    # 过滤字段
    list_filter = ('name',
                   'sign_in_support',
                   'get_userinfo_support',
                   'get_torrent_support',
                   'search_support',)
    # 搜索
    search_fields = ('name',)

    list_editable = ('sign_in_support',
                     'get_userinfo_support',
                     'get_torrent_support',
                     'search_support')

    # def has_delete_permission(self, request, obj=None):
    #     return False

    # def has_add_permission(self, request, obj=None):
    #     return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    # 自定义样式
    # def custom_date(self, obj):
    #     return format_html(
    #         '<span style="color: red;">{}</span>',
    #         obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    #     )
    # 自定义样式
    def custom_url(self, obj):
        return format_html(
            '<a style="color: red;" target="blank" href="{}">{}</span>',
            obj.url + obj.page_default,
            obj.url
        )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(SiteAdmin, self).get_search_results(request, queryset, search_term)
        if not request.META['PATH_INFO'] == '/admin/pt_site/site/':
            queryset = queryset.exclude(
                pk__in=[site.pk for site in Site.objects.all() if
                        MySite.objects.filter(site=site).count() >= 1])
        return queryset, use_distinct

    custom_url.short_description = '站点网址'
    formfield_overrides = {}
    # 分组设置编辑字段
    fieldsets = (
        ['站点设置', {
            # 'classes': ('collapse',),  # CSS
            'fields': (
                ('name', 'nickname', 'url', 'logo'),
                ('limit_speed', 'sp_full', 'tracker',),
            ),
        }],
        ['功能支持', {
            # 'classes': ('collapse',),  # CSS
            'fields': (
                ('sign_in_support', 'get_userinfo_support',),
                ('get_torrent_support', 'search_support',),
            ),
        }],
        ['签到设置', {
            'classes': ('collapse',),  # CSS
            'fields': (
                ('sign_in_captcha', 'sign_in_method',),
                ('sign_in_headers', 'sign_in_params',)
            ),
        }],
        ['站点主要页面', {
            'classes': ('collapse',),  # CSS
            'fields': (
                'page_index',
                'page_default',
                'page_sign_in',
                'page_detail',
                'page_download',
                'page_user',
                'page_control_panel',
                'page_search',
                'page_message',
                'page_leeching',
                'page_uploaded',
                'page_seeding',
                'page_completed',
                'page_mybonus',
                'page_viewfilelist',
                'page_viewpeerlist',
            ),
        }],
        ['H&R设置', {
            'classes': ('collapse',),  # CSS
            'fields': (
                'hr',
                ('hr_rate', 'hr_time',)
            ),
        }],
        ['站点信息规则', {
            'classes': ('collapse',),  # CSS
            'fields': (
                'my_uid_rule',
                'my_passkey_rule',
                'my_level_rule',
                'ratio_rule',
                'my_sp_rule',
                'hour_sp_rule',
                'my_bonus_rule',
                'invitation_rule',
                'uploaded_rule',
                'downloaded_rule',
                'seed_rule',
                'leech_rule',
                'seed_vol_rule',
                'my_hr_rule',
                'mailbox_rule',
                'notice_rule',
                'message_title',
                'notice_title',
                'notice_content',
                'full_site_free',
                'time_join_rule',
                'latest_active_rule',
            ),
        }],
        ['列表页获取规则', {
            'classes': ('collapse',),  # CSS
            'fields': (
                'torrents_rule',
                'name_rule',
                'title_rule',
                'detail_url_rule',
                'category_rule',
                'poster_rule',
                'magnet_url_rule',
                'size_rule',
                'hr_rule',
                'sale_rule',
                'sale_expire_rule',
                'release_rule',
                'seeders_rule',
                'leechers_rule',
                'completers_rule',
            ),
        }],
        ['详情页获取规则', {
            'classes': ('collapse',),  # CSS
            'fields': (
                'detail_title_rule',
                'detail_subtitle_rule',
                'detail_download_url_rule',
                'detail_size_rule',
                'detail_category_rule',
                'detail_area_rule',
                'detail_count_files_rule',
                'detail_hash_rule',
                'detail_free_rule',
                'detail_free_expire_rule',
                'detail_douban_rule',
                'detail_year_publish_rule',
            ),
        }]
    )


@admin.register(UserLevelRule)
class UserLevelRuleAdmin(AjaxAdmin):
    # 显示字段
    list_display = (
        'site',
        'level_id',
        'level',
        'days',
        # 'uploaded',
        'downloaded',
        'bonus',
        'score',
        'ratio',
        'torrents',
        # 'rights',
    )
    search_fields = ('site__name', 'level',)


class StatusInlines(TabularInlinePaginated):
    model = SiteStatus
    per_page = 10
    fields = [
        'uploaded', 'downloaded', 'ratio', 'seed', 'seed_vol', 'leech', 'invitation', 'sp_hour',
        'my_sp', 'my_bonus', 'created_at'
    ]
    # classes = ['collapse']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    # 自定义模板，删除外键显示
    template = 'admin/pt_site/inline_status/tabular.html'
    can_delete = False

    # 禁止添加按钮
    def has_add_permission(self, request, obj=None):
        return False

    # 禁止删除按钮
    # def has_delete_permission(self, request, obj=None):
    #     return False

    # 禁止修改按钮
    def has_change_permission(self, request, obj=None):
        return False


class SignInInlines(TabularInlinePaginated):
    model = SignIn
    per_page = 15

    fields = [
        'sign_in_today', 'sign_in_info',
        'created_at'
    ]
    classes = ['collapse']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    can_delete = False
    template = 'admin/pt_site/inline_status/tabular.html'

    # 自定义模板，删除外键显示
    # template = 'admin/pt_site/inline_status/tabular.html'

    # 禁止添加按钮
    def has_add_permission(self, request, obj=None):
        return False

    # 禁止删除按钮
    def has_delete_permission(self, request, obj=None):
        return False

    # 禁止修改按钮
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(MySite)
class MySiteAdmin(AjaxAdmin):  # instead of ModelAdmin
    # 显示字段
    list_display = (
        'sort_id',
        # 'user_id',
        # 'site',
        'site_name',
        # 'invitation',
        # 'my_level',
        # 'my_hr',
        'userinfo',
        'userdata',
        'leeching_seeding',
        'bonus',
        # 'time_join',
        'status_today',
        'edit',
    )
    autocomplete_fields = ('site',)
    search_fields = ('site__name', 'site__url')
    list_display_links = ['edit']
    list_editable = ['sort_id']
    ordering = ('sort_id',)
    # empty_value_display = '**'
    inlines = (
        StatusInlines,
        SignInInlines
    )

    def bonus(self, obj: MySite):
        status_today = obj.sitestatus_set.order_by('-pk').first()
        return format_html(
            '<font color="#2570a1">时魔：{} / </font>'
            '<font color="#6c4c49">魔力：{}</font><br>'
            '<font color="#708090">满魔：{} </font>'
            '<font color="#708090">积分/HP：{}</font>',
            round(float(status_today.sp_hour), 3) if status_today else 0,
            status_today.my_sp if status_today else 0,
            '{:.2%}'.format(float(status_today.sp_hour) / obj.site.sp_full) if status_today and obj.site.sp_full != 0 else 0,
            status_today.my_bonus if status_today else 0
        )

    bonus.short_description = '魔力'

    def userinfo(self, obj: MySite):
        status = obj.sitestatus_set.order_by('-pk').first()
        return format_html(
            '<font color="#2570a1">等级：{} / </font>'
            '<font color="#6c4c49">邀请：{}</font><br>'
            '<font color="Tomato">H&R：{}</font>',
            obj.my_level,
            status.invitation if status else 0,
            obj.my_hr if obj.my_hr else 0
        )

    userinfo.short_description = '用户信息'

    def userdata(self, obj: MySite):
        status_today = obj.sitestatus_set.order_by('-pk').first()
        return format_html(
            '<font color="#2570a1">已下载：{}</font> <br> <font color="#708090">已上传：{}</font>',
            FileSizeConvert.parse_2_file_size(status_today.downloaded) if status_today else 0,
            FileSizeConvert.parse_2_file_size(status_today.uploaded) if status_today else 0
        )

    userdata.short_description = '数据量'

    def leeching_seeding(self, obj: MySite):
        status_today = obj.sitestatus_set.order_by('-pk').first()
        return format_html(
            '<font color="#2570a1">做种：{}</font> / <font color="#6c4c49">下载：{} </font><br>'
            '<font color="#708090"> 做种体积：{}</font>',
            status_today.seed if status_today else 0,
            status_today.leech if status_today else 0,
            FileSizeConvert.parse_2_file_size(status_today.seed_vol) if status_today else 0,
        )

    leeching_seeding.short_description = '下载/做种'

    def edit(self, obj: MySite):
        return '编辑'

    edit.short_description = '操作'

    # 自定义更新时间，提醒今日是否更新
    def status_today(self, obj: MySite):
        is_update = obj.sitestatus_set.filter(
            updated_at__date__gte=datetime.today()
        ).first() and obj.updated_at.date() == datetime.today().date()
        signin_today = obj.signin_set.filter(created_at__date__gte=datetime.today()).first()
        if not obj.site.sign_in_support:
            signin_str = 'yes'
        else:
            signin_str = 'yes' if signin_today and signin_today.sign_in_today else 'no'
        return format_html(
            '<font size="1">签到：<img src="/static/admin/img/icon-{}.svg"><br>'
            '更新：{}<img src="/static/admin/img/icon-{}.svg"><br>'
            '<font color="#525f42">注册：{}</font></font>',
            signin_str,
            datetime.strftime(obj.updated_at, '%Y-%m-%d %H:%M:%S') if obj else '',
            'yes' if is_update else 'no',
            datetime.strftime(obj.time_join, '%Y-%m-%d %H:%M:%S') if obj.time_join else ''
        )

    status_today.short_description = '状态'

    # 签到过滤
    class SignInFilter(admin.SimpleListFilter):
        title = '今日签到'  # 过滤标题显示为"以 英雄性别"
        parameter_name = 'sign_in_state'  # 过滤器使用的过滤字段

        def lookups(self, request, model_admin):
            return (
                (False, '未签到'),
                (True, '已签到'),
            )

        def queryset(self, request, queryset):
            # print(queryset)
            signin_list = SignIn.objects.filter(
                created_at__date__gte=datetime.today(),
                sign_in_today=True
            ).all()
            # 已签到
            pk_signin_list = [signin.site.pk for signin in signin_list]
            # 加入无需签到
            pk_signin_list.extend([my_site.pk for my_site in queryset if not my_site.site.sign_in_support])
            # print(type(self.value()))
            if self.value() is None:
                return queryset
            if bool(self.value()):
                return queryset.exclude(pk__in=pk_signin_list)
            if not bool(self.value()):
                return queryset.filter(pk__in=pk_signin_list)

    # 过滤未抓取个人数据站点
    class UpdatedAtFilter(admin.SimpleListFilter):
        title = '今日刷新'  # 过滤标题显示为"以 英雄性别"
        parameter_name = 'status_today'  # 过滤器使用的过滤字段

        def lookups(self, request, model_admin):
            return (
                (0, '未刷新'),
                (1, '已刷新'),
            )

        def queryset(self, request, queryset):
            update_list = MySite.objects.filter(updated_at__date__gte=datetime.today())
            if self.value() is None:
                return queryset
            if int(self.value()) == 0:
                return queryset.exclude(pk__in=update_list)
            if int(self.value()) == 1:
                return queryset.filter(pk__in=update_list)

    list_filter = (SignInFilter, UpdatedAtFilter, 'my_level')

    def site_name(self, obj: MySite):
        template = '<div style="margin: auto 0;text-align: center"><img src="{}" style="height: 16px;weight: 16px;border-radius: 50%;"><br><a href="{}" target="_blank">{}</a></div>'
        template_badge = """<div class="el-badge item"><span style="width: 25px">{}</span><sup class="el-badge__content is-fixed">{}</sup></div>"""
        site = obj.site
        if obj.mail == 0:
            return format_html(template, site.logo, site.url, site.name)
        return format_html(template.format(site.logo, site.url, template_badge.format(site.name, obj.mail)))
        # return format_html(template_badge.format(template.format(site.logo, site.url, site.name), obj.mail))

    site_name.short_description = format_html('<a href="#">站点</a>')

    """
    def sign_in_state(self, obj: MySite):
        signin_today = obj.signin_set.filter(created_at__date__gte=datetime.today()).first()
        if not obj.site.sign_in_support:
            sign_template = '<a href="#">无需</a>'
        else:
            sign_template = '<img src="/static/admin/img/icon-{}.svg">'.format(
                'yes' if signin_today and signin_today.sign_in_today else 'no'
            )
        return format_html(sign_template)

    sign_in_state.short_description = format_html('<a href="#">签到</a>')
    """
    # def get_changeform_initial_data(self, request):
    #     print(request)
    #     return super(MySiteAdmin, self).get_changeform_initial_data(request)

    # 过滤字段
    # list_filter = ('site', 'support')
    # 顶部显示按钮
    actions = ['sign_in', 'get_status', 'get_torrents', 'sign_in_celery', 'change_user_agent']
    # 底部显示按钮
    actions_on_bottom = True

    # 尝试获取分类，但是各站差异太大
    # def get_class(self, request, queryset):
    #     for my_site in queryset:
    #         response = pt_spider.send_torrent_info_request(my_site)
    #         if response.code == 0:
    #             res = response.data
    #             classes = pt_spider.parse(res, '//*[@id="ksearchboxmain"]//td/a/img[contains(@class,"c_")]/@class')
    #             title = pt_spider.parse(res, '//*[@id="ksearchboxmain"]//td/a/img[contains(@class,"c_")]/@title')
    #             alt = pt_spider.parse(res, '//*[@id="ksearchboxmain"]//td/a/img[contains(@class,"c_")]/@alt')
    #             print(my_site.site.name)
    #             for i, j, k in zip(classes, title, alt):
    #                 print('class', i)
    #                 print('title', j)
    #                 print('alt', k)
    #             # for i in classes:
    #             #     print('class', i)
    #             # for i in title:
    #             #     print('title', i)
    #             # for i in alt:
    #             #     print('alt', i)
    #             messages.success(request, my_site.site.name)
    #         messages.error(request, my_site.site.name)

    def sign_in(self, request, queryset):
        start = time.time()
        queryset = [my_site for my_site in queryset if my_site.sign_in and
                    my_site.cookie and my_site.site.sign_in_support and
                    my_site.signin_set.filter(
                        created_at__date__gte=datetime.today(),
                        sign_in_today=True).count() <= 0]
        if len(queryset) <= 0:
            messages.success(request, '已签到或无需签到！')
        results = pool.map(pt_spider.sign_in, queryset)
        for my_site, result in zip(queryset, results):
            print(my_site, result.code)
            if result.code == StatusCodeEnum.OK.code:
                messages.success(request, '{}：{}'.format(my_site.site.name, result.msg))
            # elif result[0] == 503:
            #     messages.error(request, my_site.site.name + '签到失败！原因：5秒盾起作用了，别试了！')
            else:
                messages.error(request, '{} 签到失败！原因：{}'.format(my_site.site.name, result.msg))
        end = time.time()
        print('耗时：', end - start)

    # 显示的文本，与django admin一致
    sign_in.short_description = '签到'
    # icon，参考element-ui icon与https://fontawesome.com
    sign_in.icon = 'el-icon-star-on'
    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    sign_in.type = 'success'

    def change_user_agent(self, request, queryset):
        # 这里的queryset 会有数据过滤，只包含选中的数据
        post = request.POST
        print(post)
        # 这里获取到数据后，可以做些业务处理
        # post中的_action 是方法名
        # post中 _selected 是选中的数据，逗号分割
        if not post.get('_selected'):
            return JsonResponse(data={
                'status': 'error',
                'msg': '请先选中数据！'
            })
        else:
            res = MySite.objects.filter(pk__in=post.get('_selected').split(',')).update(
                user_agent=post.get('user_agent'))
            return JsonResponse(data={
                'status': 'success',
                'msg': f'{res}个站点成功更换UA！'
            })

    # 显示的文本，与django admin一致
    change_user_agent.short_description = '批量更换UA'
    # icon，参考element-ui icon与https://fontawesome.com
    change_user_agent.icon = 'el-icon-eleme'
    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    change_user_agent.type = 'info'

    change_user_agent.layer = {
        # 这里指定对话框的标题
        'title': '批量更换User-Agent',
        # 提示信息
        'tips': '请填写您获取Cookie时使用的浏览器的User-Agent',
        # 确认按钮显示文本
        'confirm_button': '确认提交',
        # 取消按钮显示文本
        'cancel_button': '取消',
        # 弹出层对话框的宽度，默认50%
        'width': '40%',
        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "0",
        'params': [{
            # 这里的type 对应el-input的原生input属性，默认为input
            'type': 'input',
            # key 对应post参数中的key
            'key': 'user_agent',
            # 显示的文本
            # 'label': 'UserAgent',
            # 为空校验，默认为False
            'require': True
        }]
    }

    # 获取站点个人数据
    def get_status(self, request, queryset):
        start = time.time()
        # info_list = SiteStatus.objects.filter(update_date=datetime.now().date())
        site_list = [my_site for my_site in queryset if my_site.site.get_userinfo_support]
        results = pool.map(pt_spider.send_status_request, site_list)
        message_template = MessageTemplate.status_message_template

        for my_site, result in zip(site_list, results):
            if result.code == StatusCodeEnum.OK.code:
                res = pt_spider.parse_status_html(my_site, result.data)
                # print(my_site.site, result)
                if res.code == StatusCodeEnum.OK.code:
                    site_status = res.data[0]
                    if isinstance(site_status, SiteStatus):
                        message = '{}: {}'.format(my_site.site.name,
                                                  '信息获取成功！' if res.data[1] else '信息更新成功！')
                        # status = my_site.sitestatus_set.filter(created_at__date__gte=datetime.today()).first()
                        # print(status.ratio)
                        message += message_template.format(
                            my_site.site.name,
                            my_site.my_level,
                            site_status.my_sp,
                            site_status.sp_hour,
                            site_status.my_bonus,
                            site_status.ratio,
                            FileSizeConvert.parse_2_file_size(site_status.seed_vol),
                            FileSizeConvert.parse_2_file_size(site_status.uploaded),
                            FileSizeConvert.parse_2_file_size(site_status.downloaded),
                            site_status.seed,
                            site_status.leech,
                            site_status.invitation,
                            my_site.my_hr
                        )
                        messages.success(
                            request,
                            message=message)
                    else:
                        messages.error(
                            request,
                            '{} 信息更新失败！原因：{}'.format(my_site.site.name, res.msg))
                else:
                    messages.error(
                        request,
                        '{} 信息更新失败！原因：'.format(my_site.site.name, res.msg))
            else:
                messages.error(
                    request,
                    '{} 信息更新失败！原因：'.format(my_site.site.name, result.msg))
        end = time.time()
        print('耗时：', end - start)

    get_status.short_description = '更新数据'
    # icon，参考element-ui icon与https://fontawesome.com
    get_status.icon = 'el-icon-refresh'
    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    get_status.type = 'primary'

    # 拉取种子
    def get_torrents(self, request, queryset):
        start = time.time()
        site_list = [my_site for my_site in queryset if my_site.site.get_torrent_support]
        results = pool.map(pt_spider.send_torrent_info_request, site_list)
        for my_site, result in zip(site_list, results):
            # print(result is tuple[int])
            if result.code == StatusCodeEnum.OK.code:
                # print(my_site.site, result[0].content.decode('utf8'))
                res = pt_spider.get_torrent_info_list(my_site, result.data)
                if res.code == StatusCodeEnum.OK.code:
                    messages.success(
                        request,
                        '{} 种子抓取成功！新增种子{}条，更新种子{}条：'.format(my_site.site.name, res.data[0], res.data[1])
                    )
                else:
                    messages.error(
                        request,
                        '{} 解析种子信息失败！原因：{}'.format(my_site.site.name, res.msg)
                    )
            else:
                messages.error(request, '{} 抓取种子信息失败！原因：{}'.format(my_site.site.name, result.msg))

        end = time.time()
        print('耗时：', end - start)

    # 显示的文本，与django admin一致
    get_torrents.short_description = '拉取促销种子'
    # icon，参考element-ui icon与https://fontawesome.com
    get_torrents.icon = 'el-icon-download'

    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    get_torrents.type = 'warning'

    fieldsets = (
        ['用户信息', {
            'classes': ('collapse',),  # CSS
            'fields': (
                ('site', 'sign_in', 'get_info', 'hr', 'search'),
                ('user_id', 'passkey',),
                ('time_join',),
                'user_agent',
                'cookie',
            ),
        }],
    )


"""
@admin.register(SiteStatus)
class SiteStatusAdmin(ImportExportModelAdmin):
    formats = (base_formats.XLS, base_formats.CSV, base_formats.JSON)
    list_display = ['site',
                    'upload', 'download', 'ratio',
                    'my_sp', 'my_bonus',
                    'seed_vol',
                    'updated_at']
    list_filter = ['site', 'updated_at']

    list_display_links = None

    ordering = ['site__sort_id']
    autocomplete_fields = ('site',)

    # 自定义更新时间，提醒今日是否更新
    def upload(self, obj: SiteStatus):
        return FileSizeConvert.parse_2_file_size(obj.uploaded)

    def download(self, obj: SiteStatus):
        return FileSizeConvert.parse_2_file_size(obj.downloaded)

    upload.short_description = '上传量'
    download.short_description = '下载量'

    # 禁止添加按钮
    def has_add_permission(self, request):
        return False

    # 禁止删除按钮
    # def has_delete_permission(self, request, obj=None):
    #     return False

    # 禁止修改按钮
    def has_change_permission(self, request, obj=None):
        return False

    # def changelist_view(self, request, extra_context=None):
    #     default_filter = False
    #     try:
    #         ref = request.META['HTTP_REFERER']
    #         pinfo = request.META['PATH_INFO']
    #         qstr = ref.split(pinfo)
    #         # request.META['QUERY_STRING'] = 'update_date=' + str(datetime.now().date())
    #         # print(request.GET, len(qstr))
    #         # print(pinfo, qstr, ref)
    #         # print(qstr[1].split('='))
    #         # 没有参数时使用默认过滤器
    #         if len(qstr[1].split('=')) <= 1:
    #             default_filter = True
    #         # print(request.META['QUERY_STRING'])
    #     except:
    #         default_filter = True
    #     if default_filter:
    #         q = request.GET.copy()
    #         # 添加查询参数，默认为只查询当天数据
    #         q['updated_at'] = str(datetime.now().date())
    #         # print(q)
    #         request.GET = q
    #         # print(request.GET)
    #         request.META['QUERY_STRING'] = request.GET.urlencode()
    #         # print(request.META)
    #
    #     return super(SiteStatusAdmin, self).changelist_view(request, extra_context=extra_context)
"""


@admin.register(Downloader)
class DownloaderAdmin(AjaxAdmin):  # instead of ModelAdmin
    # 显示字段
    list_display = ('name', 'category', 'reserved_space', 'created_at', 'updated_at')
    # 过滤字段
    list_filter = ('name', 'category')
    # 搜索
    search_fields = ('name', 'category')

    # 增加自定义按钮
    actions = ['test_button']

    def save_model(self, request, obj, form, change):
        obj.save()
        self.test_connect(request, obj)

    def test_button(self, request, queryset):
        for downloader in queryset:
            self.test_connect(request, downloader)

    # 连接测试
    @staticmethod
    def test_connect(request, downloader):
        try:
            conn = False
            if downloader.category == 'Tr':
                conn = transmission_rpc.Client(host=downloader.host, port=downloader.port,
                                               username=downloader.username, password=downloader.password)
            if downloader.category == 'Qb':
                qb_client = qbittorrentapi.Client(host=downloader.host, port=downloader.port,
                                                  username=downloader.username, password=downloader.password)
                qb_client.auth_log_in()
                conn = qb_client.is_logged_in
            if conn:
                messages.success(request, '{} 连接成功！'.format(downloader.name))
        except Exception as e:
            # print(e)
            messages.error(
                request,
                '连接失败！请确认下载器信息填写正确：'.format(downloader.name, e)  # 输出异常
            )
            # return False, str(e)

    # 显示的文本，与django admin一致
    test_button.short_description = '测试连接'
    # icon，参考element-ui icon与https://fontawesome.com
    test_button.icon = 'fas fa-audio-description'

    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    test_button.type = 'success'

    # 给按钮追加自定义的颜色
    # test_button.style = 'color:white;'

    # 模型保存后的操作
    # @receiver(post_save, sender=Downloader)
    # def post_save_downloader(sender, **kwargs):
    #     print(kwargs['signal'].__attr__)
    #     print(sender.test_connect(kwargs['instance']))


def get_downloader():
    """获取下载器列表"""
    try:
        return [{'key': i.id, 'label': i.name} for i in Downloader.objects.all()]
    except Exception as e:
        return []


@admin.register(TorrentInfo)
class TorrentInfoAdmin(AjaxAdmin):  # instead of ModelAdmin
    # 显示字段
    list_display = (
        'name_href',
        'title_href',
        'site',
        'state',
        'hr',
        # 'category',
        'file_size',
        'sale_status',
        'seeders',
        'leechers',
        'completers',
        'downloader',
        'd_progress',
        # 'add_a',  # 增加种子链接按钮
        'sale_expire',
        # 'updated_at'
    )

    # list_display_links = ['name_href']

    def file_size(self, torrent_info: TorrentInfo):
        return FileSizeConvert.parse_2_file_size(torrent_info.size)

    file_size.short_description = '文件大小'
    # 过滤字段
    list_filter = ('site', 'title', 'category', 'sale_status',)

    # 搜索
    search_fields = ('name', 'category')
    # 分页
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # 自定义样式
    def add_a(self, obj):
        return format_html(
            # <el-link href="{}" target="_blank">下载种子</el-link>
            # '<a target="blank" href="{}" >下载种子</a>',
            '<a href="#" target="_blank">下载种子</a>',
            obj.magnet_url
        )

    def name_href(self, obj: TorrentInfo):
        return format_html(
            # <el-link href="{}" target="_blank">下载种子</el-link>
            # '<a target="blank" href="{}" >下载种子</a>',
            '<a href="#" target="_blank" title="{}">{}</a>',
            # obj.magnet_url,
            obj.name,
            obj.name[0:25] + ' ...'
        )

    def title_href(self, obj: TorrentInfo):
        return format_html(
            # <el-link href="{}" target="_blank">下载种子</el-link>
            # '<a target="blank" href="{}" >下载种子</a>',
            '<a href="{}" target="_blank" title="{}">{}</a>',
            obj.detail_url,
            obj.title,
            obj.title[0:20] + ' ...'
        )

    def d_progress(self, obj: TorrentInfo):
        print(obj.hash_string)
        if not obj.downloader or not obj.hash_string or len(obj.hash_string) < 32:
            return 0
        progress = 0
        speed = 0
        if obj.downloader.category == DownloaderCategory.Transmission:
            tr_client = transmission_rpc.Client(
                host=obj.downloader.host,
                port=obj.downloader.port,
                username=obj.downloader.username,
                password=obj.downloader.password
            )
            print(obj.hash_string)
            torrent = tr_client.get_torrent(obj.hash_string)
            progress = torrent.progress
            print(progress)
            speed = round(torrent.rateDownload / 1024 / 1024, 2)
        if obj.downloader.category == DownloaderCategory.qBittorrent:
            pass
        if 0 < progress < 100:
            return format_html('<a href="javascript:void(0)">{} MB/s</a>', speed)
        return format_html('<a href="javascript:void(0)">{}%</a>', torrent.progress)

    # name_href.short_description = '种子名称'
    name_href.short_description = format_html(
        """
            <a href="#">{}</a>
        """, '种子名称'
    )
    title_href.short_description = '标题'
    d_progress.short_description = '下载进度'
    add_a.short_description = '下载链接'
    # 增加自定义按钮
    actions = ['to_download', 'update_state']

    # 列表推导式来获取下载器
    # downloader_list = [{'key': i.id, 'label': i.name} for i in Downloader.objects.all()]
    def update_state(self, request, queryset):
        for obj in queryset:
            tr_client = transmission_rpc.Client(
                host=obj.downloader.host,
                port=obj.downloader.port,
                username=obj.downloader.username,
                password=obj.downloader.password
            )
            torrent = tr_client.get_torrent(int(obj.hash))
            print(round(torrent.rateDownload / 1024 / 1024, 2))

    def to_download(self, request, queryset):
        # 这里的queryset 会有数据过滤，只包含选中的数据
        post = request.POST
        print(post)
        downloader = Downloader.objects.filter(id=post.get('downloader')).first()
        print(downloader)
        save_path = post.get('save_path')
        # 这里获取到数据后，可以做些业务处理
        # post中的_action 是方法名
        # post中 _selected 是选中的数据，逗号分割
        if not post.get('_selected'):
            return JsonResponse(data={
                'status': 'error',
                'msg': '请先选中数据！'
            })
        else:
            # 计算选中种子总大小，单位：字节
            total_size = 0
            for torrent_info in queryset:
                total_size += torrent_info.size
            print(FileSizeConvert.parse_2_file_size(total_size))
            if downloader.category == DownloaderCategory.Transmission:
                try:
                    # c = Client(host='192.168.123.2', port=9091, username='ngfchl', password='.wq891222')
                    # qb_client.auth_log_in()
                    # print(qb_client.torrents)
                    tr_client = transmission_rpc.Client(host=downloader.host,
                                                        port=downloader.port,
                                                        username=downloader.username,
                                                        password=downloader.password)
                    # 判断剩余空间大小，小于预留空间则停止推送种子
                    free_space = tr_client.free_space(save_path)
                    print(FileSizeConvert.parse_2_file_size(free_space))
                    if free_space < total_size:
                        return JsonResponse(data={
                            'status': 'error',
                            'msg': '{}磁盘空间已不足，下载文件总大小{}请及时清理！'.format(
                                downloader.name,
                                FileSizeConvert.parse_2_file_size(total_size)
                            )
                        })
                    if free_space <= downloader.reserved_space * 1024 * 1024 * 1024:
                        print('空间不足！')
                        return JsonResponse(data={
                            'status': 'error',
                            'msg': '{}磁盘剩余空间{}已低于保留值{}，请及时清理！'.format(
                                downloader.name,
                                FileSizeConvert.parse_2_file_size(free_space),
                                downloader.reserved_space
                            )
                        })
                    # torrent_list = [i.magnet_url for i in queryset]
                    for torrent_info in queryset:
                        # if not torrent_info.hash_string:
                        #     pt_spider.get_hash(torrent_info=torrent_info)
                        # print(qb_client.torrent_categories.categories.get(torrent.category))
                        print(torrent_info.magnet_url)
                        print(torrent_info.site.mysite.cookie)
                        # res = qb_client.torrents_add(torrent.magnet_url)
                        res = tr_client.add_torrent(
                            torrent=torrent_info.magnet_url,
                            download_dir=save_path,
                            cookies=torrent_info.site.mysite.cookie
                        )
                        print(res)
                        if isinstance(res, Torrent):
                            print(res.id)
                            torrent_info.hash_string = res.hashString
                            torrent_info.state = True
                            torrent_info.downloader = downloader
                            torrent_info.save()
                        #     return JsonResponse(data={
                        #         'status': 'success',
                        #         'msg': torrent_info.name + '推送成功！'
                        #     })
                        # else:
                    return JsonResponse(data={
                        'status': 'success',
                        'msg': '推送结束！'
                    })
                except Exception as e:
                    print(traceback.format_exc(limit=3))
                    # raise
                    return JsonResponse(data={
                        'status': 'error',
                        'msg': '{}！'.format(str(e))
                    })
            if downloader.category == DownloaderCategory.qBittorrent:
                qb_client = qbittorrentapi.Client(
                    host=downloader.host,
                    port=downloader.port,
                    username=downloader.username,
                    password=downloader.password,
                    # 仅返回简单JSON
                    # SIMPLE_RESPONSES=True
                )

                try:
                    print('开始登录下载器', downloader.name)
                    qb_client.auth_log_in()
                    # 判断剩余空间是否满足要求
                    free_space = qb_client.sync.maindata().server_state.free_space_on_disk
                    print('下载器剩余空间：', FileSizeConvert.parse_2_file_size(free_space))
                    print('种子总大小：', FileSizeConvert.parse_2_file_size(total_size))
                    if free_space <= total_size:
                        return JsonResponse(data={
                            'status': 'error',
                            'msg': '{}磁盘空间已不足，下载文件总大小{}请及时清理！'.format(
                                downloader.name,
                                FileSizeConvert.parse_2_file_size(total_size)
                            )
                        })
                    if free_space <= downloader.reserved_space * 1024 * 1024 * 1024:
                        return JsonResponse(data={
                            'status': 'error',
                            'msg': '{}磁盘剩余空间{}已低于保留值{}，请及时清理！'.format(
                                downloader.name,
                                FileSizeConvert.parse_2_file_size(free_space),
                                downloader.reserved_space
                            )
                        })
                    for torrent_info in queryset:
                        print('创建种子标签', torrent_info.detail_url)
                        # qb_client.torrents_create_category(torrent_info.detail_url)
                        res = qb_client.torrents.add(
                            # 种子链接
                            urls=torrent_info.magnet_url,
                            cookie=torrent_info.site.mysite.cookie,
                            # 保存路径
                            download_path=save_path,
                            # 自动管理种子
                            use_auto_torrent_management=True,
                            # 任务标签，用于和种子信息关联
                            # category=torrent_info.detail_url,
                            # 跳过HASH检查
                            # is_skip_checking=True
                        )
                        print(res)
                        # if res == 'Ok.':
                        # print(torrent_info.magnet_url)
                        # torrent = qb_client.torrents.info(category=torrent_info.detail_url)
                        # print(len(torrent))
                        # torrent_info.hash_string = torrent[0].hash
                        # torrent_info.save()
                        #     return JsonResponse(data={
                        #         'status': 'success',
                        #         'msg': torrent_info.name + '推送成功！'
                        #     })
                    return JsonResponse(data={
                        'status': 'success',
                        'msg': '推送结束！请自行检查是否推送成功！'
                    })
                except Exception as e:
                    return JsonResponse(data={
                        'status': 'error',
                        'msg': '{}！'.format(str(e))
                    })

    # 显示的文本，与django admin一致
    to_download.short_description = '推送到下载器'
    update_state.short_description = '更新种子'
    # icon，参考element-ui icon与https://fontawesome.com
    to_download.icon = 'el-icon-upload'
    update_state.icon = 'el-icon-refresh'
    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    to_download.type = 'warning'
    update_state.type = 'success'

    # 给按钮追加自定义的颜色
    # test_button.style = 'color:white;'

    # 这里的layer配置是动态的，可以根据需求返回不同的配置
    # 这里的queryset 或根据搜索条件来过滤数据
    # def async_get_layer_config(self, request, queryset):
    #     """
    #     这个方法只有一个request参数，没有其他的入参
    #     """
    #     # 模拟处理业务耗时
    #     time.sleep(2)
    # 可以根据request的用户，来动态设置返回哪些字段，每次点击都会来获取配置显示

    to_download.layer = {
        # 弹出层中的输入框配置
        # 这里指定对话框的标题
        'title': '推送到下载器',
        # 提示信息
        'tips': '请自行检查是否种子是否推送成功！！',
        # 确认按钮显示文本
        'confirm_button': '确认提交',
        # 取消按钮显示文本
        'cancel_button': '取消',
        # 弹出层对话框的宽度，默认50%
        'width': '40%',
        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",
        'params': [{
            'type': 'select',
            'key': 'downloader',
            'label': '下载器',
            'width': '200px',
            # size对应elementui的size，取值为：medium / small / mini
            'size': 'small',
            # value字段可以指定默认值
            'value': '',
            'require': True,
            # 列表推导式来获取下载器
            'options': get_downloader()
        }, {
            # 这里的type 对应el-input的原生input属性，默认为input
            'type': 'input',
            # key 对应post参数中的key
            'key': 'save_path',
            # 显示的文本
            'label': '保存路径',
            'value': '/downloads',
            'width': '200px',
            # 为空校验，默认为False
            'require': True
        }, ]
    }
