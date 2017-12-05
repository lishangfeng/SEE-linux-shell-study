# -*- coding:utf-8 -*-

import json
import logging
from datetime import datetime

from mssapi.s3.connection import S3Connection
from mssapi.s3.key import Key

from app.lib.utils import date_handler
from app.ssh_server.init import config
from mssapi.exception import S3ResponseError, S3CreateError


class Transport:
    def __init__(self):
        self.bucket = None
        self.conn = S3Connection(
            aws_access_key_id=config.get('mss_access'),
            aws_secret_access_key=config.get('mss_secret'),
            host=config.get('mss_server'),
            port=80
        )

    def get_bucket(self):
        bucket_name = str(datetime.now().strftime("%Y"))
        try:
            self.bucket = self.conn.get_bucket(bucket_name)
        except S3ResponseError:
            logging.warning(u'bucket: {0} 不存在, 尝试创建'.format(bucket_name))
            self.bucket = self.conn.create_bucket(bucket_name)
        except S3CreateError:
            logging.error(u'S3创建bucket: {0}失败'.format(bucket_name))
            return False
        except Exception as e:
            logging.error(u'获取 S3 bucket: {0}失败, {1}'.format(bucket_name, str(e)))
            return False
        return self.bucket

    def upload(self, remote_path, size, recorder_data):
        if config.get('app_env') != 'product':
            return
        if not self.get_bucket():
            local_path = u'/tmp/{0}'.format(recorder_data['title']) + '.json'
            open(local_path, 'w').write(json.dumps(recorder_data, ensure_ascii=False, default=date_handler))
            logging.warning(u'连接S3失败, 录像存储本地磁盘: {0}'.format(local_path))
            return False

        try:
            key = Key(self.bucket, remote_path)
            key.content_type = 'application/json'
            key.set_contents_from_string(json.dumps(recorder_data, ensure_ascii=False, default=date_handler))
            logging.info(u'上传录像到存储, {0}, {1}'.format(recorder_data['login_uuid'], size))
            return key.generate_url(expires_in=315360000)        # 链接有效期十年
        except Exception as e:
            logging.error(u'上传录像失败 {0}, {1}'.format(recorder_data['login_uuid'], str(e)))
