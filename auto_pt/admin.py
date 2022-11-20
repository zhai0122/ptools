import logging
from datetime import datetime

from apscheduler.triggers.cron import CronTrigger
from django.contrib import admin, messages
from django.http import JsonResponse
from simpleui.admin import AjaxAdmin

from auto_pt.models import Task, TaskJob, Notify, OCR
from auto_pt.views import logger
from pt_site import views as tasks
from pt_site.views import pt_spider
from ptools.base import Trigger

scheduler = tasks.scheduler


# Register your models here.


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):  # instead of ModelAdmin
    # 显示字段
    list_display = (
        'desc',
        'name',
    )
    # list_display_links = None
    search_fields = ('name',)
    readonly_fields = ('name',)

    def get_queryset(self, request):
        # print(self.kwargs['username'])
        data = [key for key in dir(tasks) if key.startswith('auto_')]
        for task in data:
            Task.objects.update_or_create(name=task, defaults={'desc': getattr(tasks, task).__doc__.strip()})
        return Task.objects.all()

    # 禁止添加按钮
    def has_add_permission(self, request):
        return False

    # 禁止删除按钮
    def has_delete_permission(self, request, obj=None):
        return False

    # 禁止修改按钮
    # def has_change_permission(self, request, obj=None):
    #     return False


@admin.register(TaskJob)
class TaskJobAdmin(admin.ModelAdmin):  # instead of ModelAdmin
    # 显示字段
    list_display = (
        'job_id',
        'task',
        'trigger',
        'task_exec',
        'replace_existing',
        'updated_at',
    )
    search_fields = ('task', 'job_id')
    list_filter = ('task', 'trigger', 'task_exec',)
    # autocomplete_fields = ('task',)
    list_editable = ('task_exec',)

    def save_model(self, request, obj: TaskJob, form, change):
        # 从字符串获取function
        func = getattr(tasks, obj.task.name)
        # 检查任务是否存在，已存在就删除任务
        exist_job = scheduler.get_job(obj.job_id)
        logger.info('当前任务：{} | {}'.format(obj.job_id, exist_job))
        try:
            if not obj.task_exec:
                logger.info(obj.job_id + '任务未开启！')
                super().save_model(request, obj, form, change)
            # else:
            # 添加任务

            if obj.trigger == Trigger.cron:
                if exist_job:
                    logger.info(obj.job_id + '任务已存在，修改中！')
                    exist_job.reschedule(trigger=CronTrigger.from_crontab(obj.expression_time))
                    logger.info(exist_job.id + '任务修改成功！')
                else:
                    logger.info(obj.job_id + ' 任务添加中！')
                    exist_job = scheduler.add_job(
                        func,
                        trigger=CronTrigger.from_crontab(obj.expression_time),
                        id=obj.job_id,
                        max_instances=1,
                        replace_existing=obj.replace_existing,
                        misfire_grace_time=obj.misfire_grace_time,
                        jitter=obj.jitter
                    )
            if obj.trigger == Trigger.interval:
                time_delta = 1
                time_str = obj.expression_time.split('*')
                for i in time_str:
                    time_delta *= int(i)
                if exist_job:
                    logger.info(obj.job_id + '任务已存在，修改中！')
                    exist_job.reschedule(trigger=obj.trigger, seconds=time_delta)
                    logger.info(exist_job.id + '任务修改成功！')
                else:
                    logger.info(obj.job_id + ' 任务添加中！')
                    exist_job = scheduler.add_job(
                        func,
                        trigger=obj.trigger,
                        id=obj.job_id,
                        seconds=time_delta,
                        max_instances=1,
                        replace_existing=obj.replace_existing,
                        misfire_grace_time=obj.misfire_grace_time,
                        jitter=obj.jitter
                    )
            logger.info('当前操作：{} 成功！'.format(exist_job))
            if not obj.task_exec:
                exist_job.pause()
            else:
                exist_job.resume()
            logger.info(obj.job_id + ' 任务暂停：' + str(exist_job.pending))
            logger.info('当前自动任务：')
            logger.info(scheduler.get_jobs())
            super().save_model(request, obj, form, change)
            messages.success(request,
                             obj.job_id + ' 保存成功！' + ('' if obj.task_exec else '如需执行任务，请勾选开启任务！'))
        except Exception as e:
            obj.task_exec = False
            obj.save()
            # raise
            msg = obj.job_id + '任务添加失败！原因：' + str(e)
            logger.error(msg)
            pt_spider.send_text('计划任务：' + msg)
            messages.error(request, msg)

    def delete_model(self, request, obj):
        print(obj)
        # DjangoJob.objects.filter(obj.job_id).delete()
        tasks.scheduler.get_job(obj.job_id).remove()
        logging.info('计划任务：' + obj.job_id + ' 取消成功！')
        pt_spider.send_text('计划任务：' + obj.job_id + ' 取消成功！')
        obj.delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            job = tasks.scheduler.get_job(obj.job_id)
            if job:
                job.remove()
            logging.info('计划任务：' + obj.job_id + ' 取消成功！')
            pt_spider.send_text('计划任务：' + obj.job_id + ' 取消成功！')
        queryset.delete()

    # def delete_view(self, request, object_id, extra_context=None):
    #     print(object_id)


@admin.register(Notify)
class NotifyAdmin(AjaxAdmin):
    list_display = [
        'name',
        'enable',
        'agentid',
        'updated_at',
    ]
    search_fields = ('name',)
    list_filter = ('name',)
    list_editable = ['enable']
    actions = ['test_notify']

    def test_notify(self, request, queryset):
        post = request.POST
        text = post.get('text')
        print(text)
        try:
            res = pt_spider.send_text(text)
            return JsonResponse(data={
                'status': 'success',
                'msg': res
            })
        except Exception as e:
            print(e)

    # 显示的文本，与django admin一致
    test_notify.short_description = '通知测试'
    # icon，参考element-ui icon与https://fontawesome.com
    test_notify.icon = 'el-icon-star-on'
    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    test_notify.type = 'warning'

    # def has_add_permission(self, request):
    #     # 保证只有一条记录
    #     count = Notify.objects.all().count()
    #     if count != 1:
    #         return True
    #     return False

    test_notify.layer = {
        # 弹出层中的输入框配置
        # 这里指定对话框的标题
        'title': '通知测试',
        # 提示信息
        'tips': '异步获取配置' + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # 确认按钮显示文本
        'confirm_button': '发送通知',
        # 取消按钮显示文本
        'cancel_button': '取消',
        # 弹出层对话框的宽度，默认50%
        'width': '40%',
        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",
        'params': [
            {
                # 这里的type 对应el-input的原生input属性，默认为input
                'type': 'input',
                # key 对应post参数中的key
                'key': 'text',
                # 显示的文本
                'label': '测试消息',
                # 为空校验，默认为False
                'require': True
            }]
    }


@admin.register(OCR)
class OCRAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'enable',
        'app_id',
        'updated_at',
    ]

    search_fields = ('name',)
    list_filter = ('name', 'enable')

    def has_add_permission(self, request):
        # 保证只有一条记录
        count = OCR.objects.all().count()
        if count != 1:
            return True
        return False
