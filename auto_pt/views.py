import json
import logging
import os
import random
import subprocess
import time
import traceback
from datetime import datetime, timedelta

import docker
import git
import qbittorrentapi
import transmission_rpc
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from pt_site.models import SiteStatus, MySite, Site, Downloader, TorrentInfo
from pt_site.views import scheduler, pt_spider
from ptools.base import CommonResponse, StatusCodeEnum, DownloaderCategory

logger = logging.getLogger('ptools')


def add_task(request):
    if request.method == 'POST':
        content = json.loads(request.body.decode())  # 接收参数
        try:
            start_time = content['start_time']  # 用户输入的任务开始时间, '10:00:00'
            start_time = start_time.split(':')
            hour = int(start_time[0])
            minute = int(start_time[1])
            second = int(start_time[2])
            s = content['s']  # 接收执行任务的各种参数
            # 创建任务
            scheduler.add_job(download_tasks.scheduler, 'cron', hour=hour, minute=minute, second=second, args=[s])
            code = '200'
            message = 'success'
        except Exception as e:
            code = '400'
            message = e

        data = {
            'code': code,
            'message': message
        }
        return JsonResponse(json.dumps(data, ensure_ascii=False), safe=False)


def get_tasks(request):
    # print(dir(tasks))
    data = [key for key in dir(download_tasks) if key.startswith('auto')]
    print(data)
    # print(tasks.__getattr__)
    # print(tasks.auto_get_status.__doc__)
    # inspect.getmembers(tasks, inspect.isfunction)
    # inspect.getmodule(tasks)
    # print(sys.modules[__name__])
    # print(sys.modules.values())
    # print(sys.modules.keys())
    # print(sys.modules.items())
    return JsonResponse('ok', safe=False)


def exec_task(request):
    # res = AutoPt.auto_sign_in()
    # print(res)
    # tasks.auto_sign_in
    return JsonResponse('ok!', safe=False)


def test_field(request):
    my_site = MySite.objects.get(pk=1)
    list1 = SiteStatus.objects.filter(site=my_site, created_at__date__gte=datetime.today())
    print(list1)
    return JsonResponse('ok!', safe=False)


def test_notify(request):
    # res = NotifyDispatch().send_text(text='66666')

    res = pt_spider.send_text('666')
    print(res)
    return JsonResponse(res, safe=False)


def do_sql(request):
    print('exit')
    return JsonResponse('ok', safe=False)


def page_downloading(request):
    return render(request, 'auto_pt/downloading.html')


def get_downloaders(request):
    downloader_list = Downloader.objects.filter(category=DownloaderCategory.qBittorrent).values('id', 'name', 'host')
    if len(downloader_list) <= 0:
        return JsonResponse(CommonResponse.error(msg='请先添加下载器！目前仅支持qBittorrent！').to_dict(), safe=False)
    return JsonResponse(CommonResponse.success(data=list(downloader_list)).to_dict(), safe=False)


def get_downloader(id):
    """根据id获取下载实例"""
    logger.info('当前下载器id：{}'.format(id))
    downloader = Downloader.objects.filter(id=id).first()
    if downloader.category == DownloaderCategory.qBittorrent:
        client = qbittorrentapi.Client(
            host=downloader.host,
            port=downloader.port,
            username=downloader.username,
            password=downloader.password,
            SIMPLE_RESPONSES=True
        )
    if downloader.category == DownloaderCategory.Transmission:
        client = transmission_rpc.Client(
            host=downloader.host, port=downloader.port,
            username=downloader.username, password=downloader.password
        )
    return client


def downloading_status(request):
    qb_list = Downloader.objects.filter(category=DownloaderCategory.qBittorrent)
    tr_list = Downloader.objects.filter(category=DownloaderCategory.Transmission)
    tr_info_list = []
    for downloader in tr_list:
        client = transmission_rpc.Client(
            host=downloader.host, port=downloader.port,
            username=downloader.username, password=downloader.password
        )
        session = transmission_rpc.session.Session(client=client)
        print(type(session))
        # print(client.get_torrents())
        session_list = client.get_session()
        session = {item: value for item, value in session_list.items()}
        tr_info = {
            # 'torrents': client.get_torrents(),
            'free_space': client.free_space('/downloads'),
            # 'session': session.values(),
            'protocol_version': client.protocol_version,
            'rpc_version': client.rpc_version,
            'session_id': client.session_id,
            # 'session_stats': client.session_stats(),
            'arguments': client.torrent_get_arguments,

        }
        tr_info_list.append(tr_info)
    return JsonResponse(CommonResponse.success(data={
        'tr_info_list': tr_info_list
    }).to_dict(), safe=False)


def get_trackers(request):
    """从已支持的站点获取tracker关键字列表"""
    tracker_list = Site.objects.all().values('id', 'name', 'tracker')
    # print(tracker_filters)
    return JsonResponse(CommonResponse.success(data={
        'tracker_list': list(tracker_list)
    }).to_dict(), safe=False)


def get_downloader_categories(request):
    id = request.GET.get('id')
    if not id:
        id = Downloader.objects.all().first().id
    qb_client = get_downloader(id)
    try:
        qb_client.auth_log_in()
        categories = [index for index, value in qb_client.torrents_categories().items()]
        logger.info('下载器{}分类：'.format(id))
        logger.info(categories)
        tracker_list = Site.objects.all().values('id', 'name', 'tracker')
        logger.info('当前支持的筛选tracker的站点：')
        logger.info(tracker_list)
        return JsonResponse(CommonResponse.success(data={
            'categories': categories,
            'tracker_list': list(tracker_list)
        }).to_dict(), safe=False)
    except Exception as e:
        logger.warning(e)
        # raise
        return JsonResponse(CommonResponse.error(
            msg='连接下载器出错咯！'
        ).to_dict(), safe=False)


def get_downloading(request):
    id = request.GET.get('id')
    logger.info('当前下载器id：{}'.format(id))
    qb_client = get_downloader(id)
    try:
        qb_client.auth_log_in()
        # transfer = qb_client.transfer_info()
        # torrents = qb_client.torrents_info()
        main_data = qb_client.sync_maindata()
        torrent_list = main_data.get('torrents')
        torrents = []
        for index, torrent in torrent_list.items():
            # print(type(torrent))
            # print(torrent)
            # torrent = json.loads(torrent)
            # 时间处理
            # 添加于
            torrent['added_on'] = datetime.fromtimestamp(torrent.get('added_on')).strftime(
                '%Y年%m月%d日%H:%M:%S'
            )
            # 完成于
            if torrent.get('downloaded') == 0:
                torrent['completion_on'] = ''
                torrent['last_activity'] = ''
                torrent['downloaded'] = ''
            else:
                torrent['completion_on'] = datetime.fromtimestamp(torrent.get('completion_on')).strftime(
                    '%Y年%m月%d日%H:%M:%S'
                )
                # 最后活动于
                last_activity = str(timedelta(seconds=time.time() - torrent.get('last_activity')))

                torrent['last_activity'] = last_activity.replace(
                    'days,', '天'
                ).replace(
                    'day,', '天'
                ).replace(':', '小时', 1).replace(':', '分', 1).split('.')[0] + '秒'
                # torrent['last_activity'] = datetime.fromtimestamp(torrent.get('last_activity')).strftime(
                #     '%Y年%m月%d日%H:%M:%S')
            # 做种时间
            seeding_time = str(timedelta(seconds=torrent.get('seeding_time')))
            torrent['seeding_time'] = seeding_time.replace('days,', '天').replace(
                'day,', '天'
            ).replace(':', '小时', 1).replace(':', '分', 1).split('.')[0] + '秒'
            # 大小与速度处理
            # torrent['state'] = TorrentBaseInfo.download_state.get(torrent.get('state'))
            torrent['ratio'] = '%.4f' % torrent.get('ratio') if torrent['ratio'] >= 0.0001 else 0
            torrent['progress'] = '%.4f' % torrent.get('progress') if float(torrent['progress']) < 1 else 1
            torrent['uploaded'] = '' if torrent['uploaded'] == 0 else torrent['uploaded']
            torrent['upspeed'] = '' if torrent['upspeed'] == 0 else torrent['upspeed']
            torrent['dlspeed'] = '' if torrent['dlspeed'] == 0 else torrent['dlspeed']
            torrent['hash'] = index
            torrents.append(torrent)
        logger.info('当前下载器共有种子：{}个'.format(len(torrents)))
        main_data['torrents'] = torrents
        return JsonResponse(CommonResponse.success(data=main_data).to_dict(), safe=False)
    except Exception as e:
        logger.error(e)
        # raise
        return JsonResponse(CommonResponse.error(
            msg='连接下载器出错咯！'
        ).to_dict(), safe=False)


def control_torrent(request):
    ids = request.POST.get('ids')
    command = request.POST.get('command')
    delete_files = request.POST.get('delete_files')
    category = request.POST.get('category')
    enable = request.POST.get('enable')
    downloader_id = request.POST.get('downloader_id')
    logger.info(request.POST)
    # print(command, type(ids), downloader_id)
    downloader = Downloader.objects.filter(id=downloader_id).first()
    qb_client = qbittorrentapi.Client(
        host=downloader.host,
        port=downloader.port,
        username=downloader.username,
        password=downloader.password,
        SIMPLE_RESPONSES=True
    )
    try:
        qb_client.auth_log_in()
        # qb_client.torrents.resume()
        # 根据指令字符串定位函数
        command_exec = getattr(qb_client.torrents, command)
        logger.info(command_exec)
        command_exec(
            torrent_hashes=ids.split(','),
            category=category,
            delete_files=delete_files,
            enable=enable, )
        # 延缓2秒等待操作生效
        time.sleep(2)
    except Exception as e:
        logger.warning(e)
    return JsonResponse(CommonResponse.success(data={
        'ids': ids.split(','),
        'command': command,
        'downloader_id': downloader_id
    }).to_dict(), safe=False)


def import_from_ptpp(request):
    if request.method == 'GET':
        return render(request, 'auto_pt/import_ptpp.html')
    else:
        data_list = json.loads(request.body).get('user')
        res = pt_spider.parse_ptpp_cookies(data_list)
        if res.code == StatusCodeEnum.OK.code:
            cookies = res.data
            # print(cookies)
        else:
            return JsonResponse(res.to_dict(), safe=False)
        message_list = []
        for data in cookies:
            try:
                # print(data)
                res = pt_spider.get_uid_and_passkey(data)
                msg = res.msg
                logger.info(msg)
                if res.code == StatusCodeEnum.OK.code:
                    message_list.append({
                        'msg': msg,
                        'tag': 'success'
                    })
                elif res.code == StatusCodeEnum.NO_PASSKEY_WARNING.code:
                    message_list.append({
                        'msg': msg,
                        'tag': 'warning'
                    })
                else:
                    # error_messages.append(msg)
                    message_list.append({
                        'msg': msg,
                        'tag': 'error'
                    })
            except Exception as e:
                message = '{} 站点导入失败！{}  \n'.format(data.get('domain'), str(e))
                message_list.append({
                    'msg': message,
                    'tag': 'warning'
                })
                # raise
            logger.info(message_list)
        return JsonResponse(CommonResponse.success(data={
            'messages': message_list
        }).to_dict(), safe=False)


def get_git_log(branch, n=20):
    repo = git.Repo(path='.')
    # 拉取仓库更新记录元数据
    repo.remote().fetch()
    # commits更新记录
    logger.info('当前分支{}'.format(branch))
    return [{
        'date': log.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        'data': log.message,
        'hexsha': log.hexsha[:16],
    } for log in list(repo.iter_commits(branch, max_count=n))]


def update_page(request):
    try:
        # 获取docker对象
        client = docker.from_env()
        # 从内部获取容器id
        cid = ''
        delta = 0
        restart = 'false'
        for c in client.api.containers():
            if 'ngfchl/ptools' in c.get('Image'):
                cid = c.get('Id')
                delta = c.get('Status')
                restart = 'true'
    except Exception as e:
        cid = ''
        restart = 'false'
        delta = '程序未在容器中启动？'

    branch = os.getenv('DEV') if os.getenv('DEV') else 'master'
    local_logs = get_git_log(branch)
    logger.info('本地代码日志{} \n'.format(local_logs))
    update_notes = get_git_log('origin/' + branch)
    logger.info('远程代码日志{} \n'.format(update_notes))
    if datetime.strptime(
            update_notes[0].get('date'), '%Y-%m-%d %H:%M:%S') > datetime.strptime(
        local_logs[0].get('date'), '%Y-%m-%d %H:%M:%S'
    ):
        update = 'true'
        update_tips = '已有新版本，请根据需要升级！'
    else:
        update = 'false'
        update_tips = '目前您使用的是最新版本！'
    return render(request, 'auto_pt/update.html',
                  context={
                      'cid': cid,
                      'delta': delta,
                      'restart': restart,
                      'local_logs': local_logs,
                      'update_notes': update_notes,
                      'update': update,
                      'update_tips': update_tips,
                      'branch': ('开发版：{}，更新于{}' if branch == 'dev' else '稳定版：{}，更新于{}').format(
                          local_logs[0].get('hexsha'), local_logs[0].get('date'))
                  })


def exec_command(commands):
    result = []
    for key, command in commands.items():
        p = subprocess.run(command, shell=True)
        logger.info('{} 命令执行结果：\n{}'.format(key, p))
        result.append({
            'command': key,
            'res': p.returncode
        })
    return result


def do_update(request):
    try:
        logger.info('开始更新')
        pt_site_site_mtime = os.stat('pt_site_site.json').st_mtime
        requirements_mtime = os.stat('requirements.txt').st_mtime
        update_commands = {
            # 'cp db/db.sqlite3 db/db.sqlite3-$(date "+%Y%m%d%H%M%S")',
            '强制覆盖本地': 'git reset --hard',
            '获取更新信息': 'git fetch --all',
            '拉取代码更新': 'git pull origin {}'.format(os.getenv('DEV')),
        }
        requirements_commands = {
            '安装依赖': 'pip install -r requirements.txt',
        }
        migrate_commands = {
            '同步数据库': 'python manage.py migrate',
        }
        logger.info('拉取最新代码')
        result = exec_command(update_commands)
        new_requirements_mtime = os.stat('requirements.txt').st_mtime
        if new_requirements_mtime > requirements_mtime:
            logger.info('更新环境依赖')
            result.extend(exec_command(requirements_commands))
        new_pt_site_site = os.stat('pt_site_site.json').st_mtime
        logger.info('更新前文件最后修改时间')
        logger.info(pt_site_site_mtime)
        logger.info('更新后文件最后修改时间')
        logger.info(new_pt_site_site)
        if new_pt_site_site == pt_site_site_mtime:
            logger.info('本次无规则更新，跳过！')
            result.append({
                'command': '本次无更新规则',
                'res': 0
            })
            pass
        else:
            logger.info('拉取更新完毕，开始更新Xpath规则')
            p = subprocess.run('cp db/db.sqlite3 db/db.sqlite3-$(date "+%Y%m%d%H%M%S")', shell=True)
            logger.info('备份数据库 命令执行结果：\n{}'.format(p))
            result.append({
                'command': '备份数据库',
                'res': p.returncode
            })
            result.extend(exec_command(migrate_commands))
            logger.info('同步数据库 命令执行结果：\n{}'.format(p))
        logger.info('更新完毕')
        return JsonResponse(data=CommonResponse.success(
            msg='更新成功，15S后自动刷新页面！',
            data={
                'result': result
            }
        ).to_dict(), safe=False)
    except Exception as e:
        # raise
        msg = '更新失败!{}，请初始化Xpath！'.format(str(e))
        logger.error(msg)
        return JsonResponse(data=CommonResponse.error(
            msg=msg
        ).to_dict(), safe=False)


def do_xpath(request):
    """初始化Xpath规则"""
    migrate_commands = {
        '备份数据库': 'cp db/db.sqlite3 db/db.sqlite3-$(date "+%Y%m%d%H%M%S")',
        '同步数据库': 'python manage.py migrate',
    }
    try:
        logger.info('开始初始化Xpath规则')
        # p = subprocess.run('cp db/db.sqlite3 db/db.sqlite3-$(date "+%Y%m%d%H%M%S")', shell=True)
        # logger.info('备份数据库 命令执行结果：\n{}'.format(p))
        # result = {
        #     'command': '备份数据库',
        #     'res': p.returncode
        # }
        result = exec_command(migrate_commands)
        logger.info('初始化Xpath规则 命令执行结果：\n{}'.format(result))
        return JsonResponse(data=CommonResponse.success(
            msg='初始化Xpath规则成功！',
            data={
                'result': result
            }
        ).to_dict(), safe=False)
    except Exception as e:
        # raise
        msg = '初始化Xpath失败!{}'.format(str(e))
        logger.error(msg)
        return JsonResponse(data=CommonResponse.error(
            msg=msg
        ).to_dict(), safe=False)


def do_restart(request):
    try:
        # 获取docker对象
        # client = docker.from_env()
        # 从内部获取容器id
        cid = request.GET.get('cid')
        # 获取容器对象
        # container = client.containers.get(cid)
        # 重启容器
        # client.api.restart(cid)
        logger.info('重启中')
        reboot = subprocess.Popen('docker restart {}'.format(cid), shell=True, stdout=subprocess.PIPE, )
        # out = reboot.stdout.readline().decode('utf8')
        # print(out)
        # client.api.inspect_container(cid)
        # StartedAt = client.api.inspect_container(cid).get('State').get('StartedAt')
        return JsonResponse(data=CommonResponse.error(
            msg='重启指令发送成功，容器重启中 ... 15秒后自动刷新页面 ...'
        ).to_dict(), safe=False)
    except Exception as e:
        return JsonResponse(data=CommonResponse.error(
            msg='重启指令发送失败!' + str(e),
        ).to_dict(), safe=False)


def render_torrents_page(request):
    """
    种子列表页
    :param request:
    :return:
    """
    return render(request, 'auto_pt/torrents.html')


def get_torrent_info_list(request):
    """
    获取种子列表
    :return:
    """
    torrent_info_list = TorrentInfo.objects.all().values()
    for torrent_info in torrent_info_list:
        if not torrent_info.downloader:
            pass
        else:
            pass


def push_to_downloader(request):
    """
    推送到下载器
    :param request:
    :return:
    """
    pass


def download_tasks():
    """
    任务管理
    :return:
    """
    downloader_list = Downloader.objects.all()
    pass


def site_status_api(request):
    try:
        userdata = get_status()
        return JsonResponse(data=CommonResponse.success(
            data=userdata
        ).to_dict(), safe=False)
    except Exception as e:
        message = f'获取数列列表失败：{e}'
        logger.info(message)
        logger.error(traceback.format_exc(limit=3))
        return CommonResponse.error(msg=message)


def get_status(ids: list = None):
    if ids is None:
        my_site_list = MySite.objects.all()
    else:
        my_site_list = MySite.objects.filter(pk__in=ids).all()
    uploaded = 0
    downloaded = 0
    seeding = 0
    seeding_size = 0
    status_list = []
    now = datetime.now()
    for my_site in my_site_list:
        site_info_list = my_site.sitestatus_set.order_by('-pk').all()
        logger.info(f'{my_site.site.name}: {len(site_info_list)}')
        if len(site_info_list) <= 0:
            logger.info(f'{my_site.site.name}: 获取站点信息列表错误！')
            continue
        site_info = site_info_list.first()
        downloaded += site_info.downloaded
        uploaded += site_info.uploaded
        seeding += my_site.seed
        seeding_size += site_info.seed_vol
        weeks = (now - my_site.time_join).days // 7
        days = (now - my_site.time_join).days % 7
        site_info = {
            'name': my_site.site.name,
            'icon': my_site.site.logo,
            'url': my_site.site.url,
            'class': my_site.my_level,
            'invite': my_site.invitation,
            'sp_hour': my_site.sp_hour,
            'sp_hour_full': '{:.2%}'.format(
                float(my_site.sp_hour) / my_site.site.sp_full) if my_site.site.sp_full != 0 else 0,
            'seeding': my_site.seed,
            'leeching': my_site.leech,
            'weeks': f'{weeks}周 {days}天',
            'time_join': my_site.time_join,
            'hr': my_site.my_hr,
            'mail': my_site.mail,
            'sp': site_info.my_sp,
            'bonus': site_info.my_bonus,
            # 'uploaded': FileSizeConvert.parse_2_file_size(site_info.uploaded),
            # 'downloaded': FileSizeConvert.parse_2_file_size(site_info.downloaded),
            # 'seeding_size': FileSizeConvert.parse_2_file_size(site_info.seed_vol),
            'uploaded': site_info.uploaded,
            'downloaded': site_info.downloaded,
            'seeding_size': site_info.seed_vol,
        }
        status_list.append(site_info)
    # 按上传量排序
    # status_list.sort(key=lambda x: x['mail'], reverse=False)
    # status_list.sort(key=lambda x: x['mail'], reverse=True)
    # sorted(status_list, key=lambda x: x['uploaded'])
    # 随机乱序
    # random.shuffle(status_list)
    total_data = {
        # 'uploaded': FileSizeConvert.parse_2_file_size(uploaded),
        # 'downloaded': FileSizeConvert.parse_2_file_size(downloaded),
        # 'seeding_size': FileSizeConvert.parse_2_file_size(seeding_size),
        'uploaded': uploaded,
        'downloaded': downloaded,
        'seeding_size': seeding_size,
        'seeding': seeding,
        'ratio': round(uploaded / downloaded, 3),
    }
    # return render(request, 'auto_pt/status.html')
    return {
        'total_data': total_data,
        'status_list': status_list
    }


@login_required
def site_status(request):
    return render(request, 'auto_pt/status.html')


def user_data(request):
    my_site_list = MySite.objects.all()

    return render(request, 'auto_pt/userdata.html')
