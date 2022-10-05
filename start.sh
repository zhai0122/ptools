#!/bin/bash
CONTAINER_ALREADY_STARTED="CONTAINER_ALREADY_STARTED_PLACEHOLDER"
if [[ $DEV == dev ]]; then
  echo "您当前处于开发版本，请注意备份文件"
else
  echo "您当前处于稳定版本"
fi
if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
  echo "-- First container startup --"
  echo "升级pip"
  python -m pip install --upgrade pip
  # 此处插入你要执行的命令或者脚本文件
  echo "下载PTools代码"
  git init &&
    git remote add origin https://gitee.com/ngfchl/ptools &&
    # 设置拉取最新文件并覆盖
    git config pull.ff only &&
    git pull origin $DEV
  echo "列出代码文件信息"
  ls -l && pwd
  echo "安装pip依赖"
  pip install -r requirements.txt -U
  echo "初始化数据库"
  python manage.py makemigrations
  python manage.py migrate
  python manage.py loaddata pt.json
  echo "创建超级用户"
  DJANGO_SUPERUSER_USERNAME=$DJANGO_SUPERUSER_USERNAME \
    DJANGO_SUPERUSER_EMAIL=$DJANGO_SUPERUSER_EMAIL \
    DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD \
    python manage.py createsuperuser --noinput
  echo "初始化完成"
  touch $CONTAINER_ALREADY_STARTED
else
  echo "-- Not first container startup --"
fi
echo "启动服务"
python manage.py runserver 0.0.0.0:$DJANGO_WEB_PORT >>/var/www/html/ptools/db/$(date "+%Y%m%d").log 2>&1
