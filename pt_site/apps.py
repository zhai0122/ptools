import json
import logging

from django.apps import AppConfig

from ptools.settings import BASE_DIR

logger = logging.getLogger('ptools')


class PtSiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pt_site'
    verbose_name = 'PT站点管理'

    def ready(self):
        from pt_site.models import Site
        logger.info('初始化站点信息')
        try:
            with open('pt_site_site.json', 'r') as f:
                # print(f.readlines())
                data = json.load(f)
                logger.info('更新规则中，返回结果为True为新建，为False为更新，其他是错误了')
                for site_rules in data:
                    if site_rules.get('pk'):
                        del site_rules['pk']
                    if site_rules.get('id'):
                        del site_rules['id']
                    site_obj = Site.objects.update_or_create(defaults=site_rules, url=site_rules.get('url'))
                    msg = site_obj[0].name + (' 规则新增成功！' if site_obj[1] else '规则更新成功！')
                    logger.info(msg)
        except Exception as e:
            logger.error('初始化站点信息出错！{}'.format(e))
