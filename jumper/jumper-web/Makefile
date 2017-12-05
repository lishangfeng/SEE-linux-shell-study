SHELL := /bin/bash
PATH  := node_modules/.bin:$(PATH)
VIRTUALENV_DIR := .venv
EXEC := ${VIRTUALENV_DIR}/bin/python ${VIRTUALENV_DIR}/bin/gunicorn -c gun.py app.main:app
EXEC_LOCAL := ${VIRTUALENV_DIR}/bin/python ${VIRTUALENV_DIR}/bin/gunicorn -c gun-local.py app.main:app

help:
	@echo "  server      启动 web server"
	@echo "  install     初始化前后端环境"
	@echo "  shell       打开一个加载应用上下文的 shell"
	@echo "  pip         仅初始化后端 python 环境"
	@echo "  npm         仅初始化前端 nodejs 环境"
	@echo "  daemon      用gunicorn开启程序"
	@echo "  status      查看当前开启的进程"
	@echo "  stop        关闭gunicorn进程"
	@echo "  url         url 列表"
	@echo "  clean       清理 .pyc 文件"
	@echo "  config      查看当前服务配置项"
	@echo -e "  \033[0;31m-------以下为危险命令-------\033[0m"
	@echo -e "  \033[0;31mflush-nss         刷新nss缓存\033[0m"
	@echo -e "  \033[0;31mflush-host        刷新host缓存\033[0m"
	@echo -e "  \033[0;31mflush-sudo        刷新sudo缓存\033[0m"
	@echo -e "  \033[0;31msync-cache        校准redis所有缓存数据\033[0m"
	@echo -e "  \033[0;31msync-mysql        校准mysql部分表数据\033[0m"
	@echo -e "  \033[0;31msync-userinfo     校准用户表企业系统信息\033[0m"
	@echo -e "  \033[0;31mclean-expired     清理mysql中过期授权和sudo\033[0m"
	@echo -e "  \033[0;31mupload            上传repair-jumper脚本\033[0m"
	@echo -e "  \033[0;31mtmp               创建临时账户，修改tools目录下tmp_account.py文件\033[0m"

i install: npm pip

flush-nss:
	$(VIRTUALENV_DIR)/bin/python manage.py flush-nss
flush-host:
	$(VIRTUALENV_DIR)/bin/python manage.py flush-host
flush-sudo:
	$(VIRTUALENV_DIR)/bin/python manage.py flush-sudo
sync-cache:
	$(VIRTUALENV_DIR)/bin/python manage.py sync-cache
sync-mysql:
	$(VIRTUALENV_DIR)/bin/python manage.py sync-mysql
sync-userinfo:
	$(VIRTUALENV_DIR)/bin/python manage.py sync-userinfo
clean-expired:
	$(VIRTUALENV_DIR)/bin/python manage.py clean-expired
config:
	$(VIRTUALENV_DIR)/bin/python manage.py config
upload:
	$(VIRTUALENV_DIR)/bin/python manage.py upload
tmp:
	$(VIRTUALENV_DIR)/bin/python manage.py tmp

npm:
	npm install
	bower install 
	grunt copy

pip:
	pip install virtualenv
	virtualenv $(VIRTUALENV_DIR)
	$(VIRTUALENV_DIR)/bin/pip install -r requirements.txt
	mkdir -p instance
	mkdir -p data
	touch instance/config.py

daemon:
	${EXEC_LOCAL}
	ps aux | grep -v grep | grep --colour=auto "${EXEC_LOCAL}"

status:
	ps aux | grep -v grep | grep --colour=auto "${EXEC}"

stop:
	cat gunicorn.pid|xargs kill

dev:
	$(VIRTUALENV_DIR)/bin/python manage.py dev

s server:
	$(VIRTUALENV_DIR)/bin/python manage.py server

shell:
	$(VIRTUALENV_DIR)/bin/pip install ipython
	$(VIRTUALENV_DIR)/bin/python manage.py shell

url:
	$(VIRTUALENV_DIR)/bin/python manage.py url

clean:
	$(VIRTUALENV_DIR)/bin/python manage.py clean

db:
	$(VIRTUALENV_DIR)/bin/python manage.py db $(ARG)

#.PHONY: docs test
