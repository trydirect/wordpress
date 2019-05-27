#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import docker
import requests

client = docker.from_env()

time.sleep(20)

for c in client.containers.list():
    print(c.name)
    print(c.status)
    if 'running' not in c.status:
        print(c.logs())

# NGINX
nginx = client.containers.get('nginx')
nginx_cfg = nginx.exec_run("/usr/sbin/nginx -T")
assert nginx.status == 'running'
# print(nginx_cfg.output.decode())
assert 'server_name _;' in nginx_cfg.output.decode()
assert "error_log /proc/self/fd/2" in nginx_cfg.output.decode()
assert "location = /.well-known/acme-challenge/" in nginx_cfg.output.decode()
assert 'HTTP/1.1" 500' not in nginx.logs()

# test restart
nginx.restart()
time.sleep(3)
assert nginx.status == 'running'

# Symfony PHP
php = client.containers.get('wordpress')
assert php.status == 'running'
php_conf = php.exec_run("php-fpm7.0 -t")
# print(php_conf.output.decode())
assert 'configuration file /etc/php/7.0/fpm/php-fpm.conf test is successful' in php_conf.output.decode()
php_proc = php.exec_run("sh -c 'ps aux |grep php-fpm'")
print(php_proc.output.decode())
assert 'php-fpm: master process (/etc/php/7.0/fpm/php-fpm.conf)' in php_proc.output.decode()
assert 'wordpre+' in php_proc.output.decode()
assert 'php-fpm: pool www' in php_proc.output.decode()
assert 'fpm is running, pid' in php.logs()

mysql = client.containers.get('wpdb')
assert mysql.status == 'running'
mycnf = mysql.exec_run("/usr/sbin/mysqld --verbose  --help")
# print(mycnf.output.decode())
print(mysql.logs())
mysql_log = mysql.logs()
assert "Version: '5.7.26'" in mysql_log
assert "mysqld: ready for connections" in mysql_log.decode()

response = requests.get("http://localhost")
assert response.status_code == 200
print(response.text)
assert 'Welcome to the famous five-minute WordPress installation process!' in response.text
