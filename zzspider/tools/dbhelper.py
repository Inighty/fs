# ！/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging

import pymysql

from zzspider import settings
from zzspider.tools.singleton_type import Singleton

logger = logging.getLogger(__name__)


class DBHelper(metaclass=Singleton):
    # 构造函数
    def __init__(self, host=settings.MYSQL_HOST, user=settings.MYSQL_USER,
                 pwd=settings.MYSQL_PASSWD, db=settings.MYSQL_DBNAME):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.conn = None
        self.cur = None
        self.connect_database()

    # 连接数据库
    def connect_database(self):
        try:
            self.conn = pymysql.connect(self.host, self.user,
                                        self.pwd, self.db, charset='utf8mb4')
        except:
            logger.error("connectDatabase failed")
            return False
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
        return True

    # 关闭数据库
    def close(self):
        # 如果数据打开，则关闭；否则没有操作
        if self.conn and self.cur:
            self.cur.close()
            self.conn.close()
        return True

    # 执行数据库的sq语句,主要用来做插入操作
    def execute(self, sql, params=None):
        try:
            if self.conn and self.cur:
                # 正常逻辑，执行sql，提交操作
                self.cur.execute(sql, params)
                self.conn.commit()
        except Exception as e:
            logger.error("execute failed: " + sql)
            logger.error("params: " + ' '.join(params))
            logger.error(e)
            self.close()
            return False
        return True

    # 用来查询表数据
    def fetch_all(self, sql, params=None):
        self.execute(sql, params)
        return self.cur.fetchall()

    # 用来查询表数据
    def fetch_one(self, sql, params=None):
        self.execute(sql, params)
        return self.cur.fetchone()
