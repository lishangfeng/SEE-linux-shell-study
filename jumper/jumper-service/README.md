## jumper-service

### 配置环境
1. make pip
安装虚拟环境, 并安装相关依赖


### 配置文件
1. 优先级
配置文件优先级(即加载顺序)  config.py -> lion -> instance/config.py
2. lion读取
以应用名称(app_name)和所属环境(app_env)请求lion接口, 读取配置


### 启动方式
1. 前台启动方式
make s

2. 后台启动方式(将以daemon进程在后台工作)
python main.py background

3. 启动脚本
cp init.d/jumper-server /etc/init.d/jumper-server
chkconfig --add jumper-server
service jumper-server start
