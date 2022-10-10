# 先备份数据库文件再拉取更新 $(date "+%Y%m%d%H%M%S")当前时间年月日时分秒
cp /ptools/db/db.sqlite3 /ptools/db/db.sqlite3-$(date "+%Y%m%d%H%M%S")
git pull
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
