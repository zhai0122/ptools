#!/bin/bash
CONTAINER_ALREADY_STARTED="CONTAINER_ALREADY_STARTED_PLACEHOLDER"
if [[ $DEV == dev ]]; then
  echo "您当前处于开发版本，请注意备份文件"
else
  echo "您当前处于稳定版本"
fi
if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
  echo "-- First container startup --"
  # 此处插入你要执行的命令或者脚本文件
  echo "升级pip"
  python -m pip install --upgrade pip
  echo "拉取PTools最新代码"
  # 设置拉取最新文件并覆盖
  git config pull.ff only
  git checkout $DEV
  echo "系统初始化中"
  python manage.py migrate
  touch $CONTAINER_ALREADY_STARTED
  echo "创建超级用户"
  DJANGO_SUPERUSER_USERNAME=$DJANGO_SUPERUSER_USERNAME
  DJANGO_SUPERUSER_EMAIL=$DJANGO_SUPERUSER_EMAIL
  DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD
  python manage.py createsuperuser --noinput
  echo "初始化完成"
else
  echo "-- Not first container startup --"
fi
echo "拉取PTools最新代码"
git pull
git pull origin $DEV
echo "列出代码文件信息"
ls -l
echo "安装并升级pip依赖"
pip install -r requirements.txt -U
if [ ! -f db/hosts ]; then
  echo "未自定义HOSTS，默认写入"
  echo 172.64.153.252 u2.dmhy.org >>/etc/hosts
  echo 104.25.26.31 u2.dmhy.org >>/etc/hosts
  echo 104.25.61.106 u2.dmhy.org >>/etc/hosts
  echo 104.25.62.106 u2.dmhy.org >>/etc/hosts
  echo 172.67.98.15 u2.dmhy.org >>/etc/hosts
else
  echo '存在自定义HOSTS文件，apply'
  cp -f db/hosts /etc/hosts
fi
echo "启动服务"
python manage.py migrate
python manage.py runserver 0.0.0.0:$DJANGO_WEB_PORT
