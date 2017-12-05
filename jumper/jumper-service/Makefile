SHELL := /bin/bash
VIRTUALENV_DIR = .venv

help:
	@echo "  start       启动 jumper-server"
	@echo "  config      显示项目配置"
	@echo "  pip         仅初始化后端 python 环境"
	@echo "  更多请查看README.md"

pip:
	pip install virtualenv
	virtualenv $(VIRTUALENV_DIR)
	$(VIRTUALENV_DIR)/bin/pip install -r requirements.txt
	mkdir -p instance
	mkdir -p data
	touch instance/config.py

s start:
	@if [ -f /opt/rh/python27/enable ];then\
		source /opt/rh/python27/enable;\
		$(VIRTUALENV_DIR)/bin/python manage.py;\
	else\
		$(VIRTUALENV_DIR)/bin/python manage.py;\
	fi

config:
	@if [ -f /opt/rh/python27/enable ];then\
		source /opt/rh/python27/enable;\
		$(VIRTUALENV_DIR)/bin/python app/ssh_server/init.py;\
	else\
		$(VIRTUALENV_DIR)/bin/python app/ssh_server/init.py;\
	fi

#.PHONY: docs test
